import grpc
from pydantic import ValidationError
import yaml
import logging
import traceback
from concurrent import futures
from typing import Any

from google.protobuf import struct_pb2
from google.protobuf.json_format import MessageToDict, ParseDict

from . import common_pb2, command_pb2, playbook_pb2, attackmate_service_pb2_grpc

from attackmate.attackmate import AttackMate
from attackmate.playbook_parser import parse_config
from attackmate.schemas.playbook import Playbook
from attackmate.command import CommandRegistry
from attackmate.variablestore import VariableStore
from attackmate.logging_setup import (
    initialize_logger,
    initialize_output_logger,
    initialize_json_logger,
)
from attackmate.result import Result as AttackMateResult
from attackmate.execexception import ExecException
from attackmate.schemas.config import Config

# Configure logging for the server
logging.basicConfig(
    level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


# Helper Functions#
def _value_to_protobuf(value: Any) -> common_pb2.VariableValue:
    """Converts a Python value to a Protobuf VariableValue."""
    pb_value = common_pb2.VariableValue()
    if value is None:
        pb_value.null_value = struct_pb2.NULL_VALUE
    elif isinstance(value, bool):
        pb_value.bool_value = value
    elif isinstance(value, (int, float)):
        pb_value.number_value = value
    elif isinstance(value, str):
        pb_value.string_value = value
    elif isinstance(value, dict):
        ParseDict(value, pb_value.struct_value)
    elif isinstance(value, list):
        ParseDict(value, pb_value.list_value)
    else:
        # Fallback to string representation for unknown types
        pb_value.string_value = str(value)
        logger.warning(f"Unsupported type {type(value)} converted to string: {value}")
    return pb_value


def _protobuf_to_value(pb_value: common_pb2.VariableValue) -> Any:
    """Converts a Protobuf VariableValue back to a Python value."""
    if pb_value.HasField('string_value'):
        return pb_value.string_value
    elif pb_value.HasField('number_value'):
        # Return as int if it's a whole number, else float?
        num = pb_value.number_value
        return int(num) if num == int(num) else num
    elif pb_value.HasField('bool_value'):
        return pb_value.bool_value
    elif pb_value.HasField('struct_value'):
        return MessageToDict(pb_value.struct_value)
    elif pb_value.HasField('list_value'):
        return MessageToDict(pb_value.list_value)
    elif pb_value.HasField('null_value'):
        return None
    return None


def _varstore_to_protobuf(varstore: VariableStore) -> common_pb2.VariableStoreState:
    """Converts an AttackMate VariableStore to Protobuf VariableStoreState."""
    state = common_pb2.VariableStoreState()
    combined_vars = {}
    # string variables
    for key, value in varstore.variables.items():
        combined_vars[key] = value
    # list variables
    for key, value in varstore.lists.items():
        combined_vars[key] = value

    for key, value in combined_vars.items():
        state.variables[key].CopyFrom(_value_to_protobuf(value))

    return state


def _protobuf_to_varstore(
    state: common_pb2.VariableStoreState, varstore: VariableStore
):
    """Populates an AttackMate VariableStore from Protobuf VariableStoreState."""
    varstore.clear()
    for key, pb_value in state.variables.items():
        value = _protobuf_to_value(pb_value)
        # set_variable distinguishes between lists and strings automatically
        varstore.set_variable(key, value)


def _proto_command_to_pydantic(proto_cmd: command_pb2.Command):
    """Converts a Protobuf Command message to a Pydantic Command model."""
    logger.debug(
        f"Converting protobuf command: type='{proto_cmd.type}', cmd='{proto_cmd.cmd}'"
    )

    # Extract parameters from the Struct
    params_dict = (
        MessageToDict(proto_cmd.parameters) if proto_cmd.HasField('parameters') else {}
    )
    logger.debug(f"Extracted parameters dict: {params_dict}")

    # Add common fields from the proto message if they are set
    common_fields = {
        'only_if': proto_cmd.only_if if proto_cmd.HasField('only_if') else None,
        'error_if': proto_cmd.error_if if proto_cmd.HasField('error_if') else None,
        'error_if_not': (
            proto_cmd.error_if_not if proto_cmd.HasField('error_if_not') else None
        ),
        'loop_if': proto_cmd.loop_if if proto_cmd.HasField('loop_if') else None,
        'loop_if_not': (
            proto_cmd.loop_if_not if proto_cmd.HasField('loop_if_not') else None
        ),
        'loop_count': (
            proto_cmd.loop_count if proto_cmd.HasField('loop_count') else None
        ),  # Keep as string
        'exit_on_error': (
            proto_cmd.exit_on_error if proto_cmd.HasField('exit_on_error') else None
        ),
        'save': proto_cmd.save if proto_cmd.HasField('save') else None,
        'background': (
            proto_cmd.background if proto_cmd.HasField('background') else None
        ),
        'kill_on_exit': (
            proto_cmd.kill_on_exit if proto_cmd.HasField('kill_on_exit') else None
        ),
        'metadata': dict(proto_cmd.metadata) if proto_cmd.metadata else None,
    }
    # Filter out None values so Pydantic defaults apply correctly
    common_fields_filtered = {k: v for k, v in common_fields.items() if v is not None}

    # Combine everything
    combined_data = {
        'type': proto_cmd.type,
        'cmd': proto_cmd.cmd,
        **params_dict,
        **common_fields_filtered,
    }
    logger.debug(f"Combined data for Pydantic model: {combined_data}")

    try:
        # Find the correct Pydantic command class
        CommandClass = CommandRegistry.get_command_class(proto_cmd.type, proto_cmd.cmd)
        if CommandClass is None:
            # Fallback if cmd is not part of the registration key
            CommandClass = CommandRegistry.get_command_class(proto_cmd.type)

        if CommandClass is None:
            raise ValueError(
                f"Could not find Pydantic model for type='{proto_cmd.type}', cmd='{proto_cmd.cmd}'"
            )

        logger.debug(f"Found Pydantic class: {CommandClass.__name__}")

        # Create and validate the Pydantic model
        pydantic_cmd = CommandClass.model_validate(combined_data)
        logger.debug(f"Successfully created Pydantic command: {pydantic_cmd}")
        return pydantic_cmd
    except (ValidationError, ValueError, KeyError) as e:
        logger.error(
            f"Error converting protobuf command to Pydantic: {e}\nData: {combined_data}"
        )
        logger.error(traceback.format_exc())
        raise ValueError(f"Failed to create Pydantic command: {e}") from e
    except Exception as e:
        logger.error(
            f"Unexpected error during Pydantic conversion: {e}\nData: {combined_data}"
        )
        logger.error(traceback.format_exc())
        raise ValueError(f"Unexpected error creating Pydantic command: {e}") from e


# Servicer Implementation


class AttackMateServiceImpl(attackmate_service_pb2_grpc.AttackMateServiceServicer):
    """Implements the AttackMate gRPC service."""

    def __init__(self, config: Config):
        self.config = config
        # Initialize global loggers here?
        # Initialize core AttackMate instance - THIS MAINTAINS THE STATE between ExecuteCommand calls
        # TODO  assumes thread safety --> check if this does work
        # otherwise handle requests sequentially? worker count 1?
        logger.info('Initializing persistent AttackMate instance for the server...')
        # Create a dummy initial playbook for the persistent instance
        initial_playbook = Playbook(commands=[], vars={})
        self.attackmate_instance = AttackMate(
            playbook=initial_playbook, config=self.config, varstore={}
        )
        logger.info('Persistent AttackMate instance initialized.')

    def ExecutePlaybook(
        self, request: playbook_pb2.ExecutePlaybookRequest, context
    ) -> playbook_pb2.ExecutePlaybookResponse:
        """Handles requests to execute a full playbook."""
        logger.info('Received ExecutePlaybook request.')
        response = playbook_pb2.ExecutePlaybookResponse()

        try:
            playbook_yaml_str = request.playbook_yaml
            if not playbook_yaml_str:
                raise ValueError('Playbook YAML content cannot be empty.')

            # Parse
            playbook_dict = yaml.safe_load(playbook_yaml_str)
            if not playbook_dict:
                raise ValueError('Playbook YAML not parsed successfully.')

            logger.info('Playbook YAML parsed successfully.')

            # Validate
            playbook = Playbook.model_validate(playbook_dict)
            logger.info('Playbook validated successfully.')

            # Create an AttackMate instance for this specific playbook execution -> isolated state for each full playbook run
            logger.info(
                'Creating transient AttackMate instance for playbook execution...'
            )
            initial_vars = {}
            temp_vs = VariableStore()  # Create temporary varstore to load initial state
            if request.HasField('initial_state'):
                _protobuf_to_varstore(request.initial_state, temp_vs)
                # Combine string and list vars for AttackMate constructor
                initial_vars.update(temp_vs.variables)
                initial_vars.update(temp_vs.lists)

            am_instance = AttackMate(
                playbook=playbook, config=self.config, varstore=initial_vars
            )
            logger.info('Transient AttackMate instance created.')

            # Execute  playbook
            logger.info('Executing playbook...')
            # am_instance.main() is blocking
            return_code = am_instance.main()
            logger.info(f"Playbook execution finished with code: {return_code}")

            response.success = return_code == 0
            response.message = 'Playbook execution finished.'
            response.final_state.CopyFrom(_varstore_to_protobuf(am_instance.varstore))

        except (yaml.YAMLError, ValidationError, ValueError) as e:
            error_msg = f"Error processing playbook: {e}"
            logger.error(error_msg)
            logger.error(traceback.format_exc())
            response.success = False
            response.message = error_msg
            context.set_code(grpc.StatusCode.INVALID_ARGUMENT)
            context.set_details(error_msg)
        except Exception as e:
            error_msg = f"Unexpected error during playbook execution: {e}"
            logger.error(error_msg)
            logger.error(traceback.format_exc())
            response.success = False
            response.message = error_msg
            context.set_code(grpc.StatusCode.INTERNAL)
            context.set_details(error_msg)

        return response

    def ExecuteCommand(
        self, request: command_pb2.ExecuteCommandRequest, context
    ) -> command_pb2.ExecuteCommandResponse:
        """Handles requests to execute a single command using the persistent server state."""
        logger.info(
            f"Received ExecuteCommand request for type: {request.command.type}, cmd: {request.command.cmd}"
        )
        response = command_pb2.ExecuteCommandResponse()
        response.result.success = False  # Default

        try:
            # Convert Protobuf Command to Pydantic Command
            pydantic_cmd = _proto_command_to_pydantic(request.command)
            logger.info(
                f"Successfully converted proto command to Pydantic: {pydantic_cmd.type} - {pydantic_cmd.cmd}"
            )

            # Execute the command using the persistent AttackMate instance
            logger.info('Executing command using persistent AttackMate instance...')
            try:
                # run_command executes a single step
                attackmate_result: AttackMateResult = (
                    self.attackmate_instance.run_command(pydantic_cmd)
                )

                # run_command returns Result(None, None) for background tasks or skipped conditionals
                if (
                    attackmate_result.stdout is None
                    and attackmate_result.returncode is None
                ):
                    logger.info(
                        'Command resulted in None (backgrounded or skipped), reporting success.'
                    )
                    response.result.success = True
                    response.result.stdout = 'Command backgrounded or skipped'
                    response.result.returncode = 0
                else:
                    response.result.success = True  # gRPC call succeeded
                    response.result.stdout = (
                        str(attackmate_result.stdout)
                        if attackmate_result.stdout is not None
                        else ''
                    )
                    response.result.returncode = (
                        int(attackmate_result.returncode)
                        if attackmate_result.returncode is not None
                        else -1
                    )  # Indicate missing RC

                logger.info(
                    f"Command execution finished. RC: {response.result.returncode}, Stdout beginn: '{response.result.stdout[:100]}...'"
                )

            except ExecException as e:
                error_msg = f"AttackMate execution error: {e}"
                logger.error(error_msg)
                response.result.success = False  # Execution failed
                response.result.error_message = error_msg
            except SystemExit as e:
                # Catch exit(1) calls from executors
                error_msg = f"Command triggered SystemExit (code {e.code}), likely due to error condition (exit_on_error, error_if)."
                logger.error(error_msg)
                response.result.success = False
                response.result.stdout = (
                    response.result.stdout + f"\nERROR: {error_msg}"
                )  # Append error info
                response.result.returncode = e.code if isinstance(e.code, int) else 1
                response.result.error_message = error_msg
            except Exception as e:
                # Catch unexpected errors during the run_command call itself
                error_msg = f"Unexpected error during command run: {e}"
                logger.error(error_msg)
                logger.error(traceback.format_exc())
                response.result.success = False
                response.result.error_message = error_msg
                context.set_code(grpc.StatusCode.INTERNAL)
                context.set_details(error_msg)

            # Get the updated VariableStore state
            logger.debug('Retrieving updated variable store state...')
            response.updated_state.CopyFrom(
                _varstore_to_protobuf(self.attackmate_instance.varstore)
            )
            logger.debug('Variable store state updated in response.')

        except (ValidationError, ValueError) as e:
            error_msg = f"Error processing command request: {e}"
            logger.error(error_msg)
            logger.error(traceback.format_exc())
            response.result.success = False
            response.result.error_message = error_msg
            context.set_code(grpc.StatusCode.INVALID_ARGUMENT)
            context.set_details(error_msg)
        except Exception as e:
            error_msg = f"Unexpected error during command execution: {e}"
            logger.error(error_msg)
            logger.error(traceback.format_exc())
            response.result.success = False
            response.result.error_message = error_msg
            context.set_code(grpc.StatusCode.INTERNAL)
            context.set_details(error_msg)

        return response

    def cleanup(self):
        """Cleans up resources when the server shuts down."""
        logger.warning('Server shutting down. Cleaning up AttackMate instance...')
        try:
            self.attackmate_instance.clean_session_stores()
            self.attackmate_instance.pm.kill_or_wait_processes()
            logger.info('AttackMate cleanup finished.')
        except Exception as e:
            logger.error(f"Error during AttackMate cleanup: {e}")
            logger.error(traceback.format_exc())


# Server Startup


def serve():
    """Starts the gRPC server."""
    # Initialize loggers
    # configure via the main AttackMate config file?
    # TODO make configurable via command line arguments when starting up server
    initialize_logger(debug=True, append_logs=False)
    initialize_output_logger(debug=True, append_logs=False)
    initialize_json_logger(json=True, append_logs=False)
    logger.info('AttackMate loggers initialized.')

    # Load AttackMate configuration
    # Using None for config file path, so it searches default locations
    # Pass server's logger instance
    attackmate_config = parse_config(config_file=None, logger=logger)
    logger.info('AttackMate configuration loaded.')

    # Create gRPC server
    # ThreadPoolExecutor for handling requests concurrently?
    #  max_workers=1 for sequential execution?
    server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))

    # Create Servicer instance
    servicer = AttackMateServiceImpl(attackmate_config)

    # Add Servicer to server
    attackmate_service_pb2_grpc.add_AttackMateServiceServicer_to_server(
        servicer, server
    )

    # Define listening port
    port = 50051
    listen_addr = f"[::]:{port}"
    # TODO secure port in production
    server.add_insecure_port(listen_addr)
    logger.info(f"Starting AttackMate gRPC server on {listen_addr}")
    server.start()

    try:
        server.wait_for_termination()
    except KeyboardInterrupt:
        logger.warning('KeyboardInterrupt received. Shutting down server...')
    finally:
        servicer.cleanup()
        server.stop(grace=5).wait()
        logger.info('Server shut down.')


if __name__ == '__main__':
    serve()
