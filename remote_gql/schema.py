import sys
import strawberry
import yaml
import logging
from typing import Optional, Dict, Any

# for flexible variable values
from strawberry.scalars import JSON
from strawberry.types import Info

from attackmate.attackmate import AttackMate
from attackmate.schemas.playbook import Playbook
from attackmate.command import CommandRegistry
from attackmate.variablestore import VariableStore
from attackmate.execexception import ExecException
from pydantic import ValidationError


logger = logging.getLogger(__name__)


@strawberry.type
class CommandResult:
    """Result of a single command execution."""
    success: bool
    stdout: Optional[str] = None
    returncode: Optional[int] = None
    error_message: Optional[str] = None


@strawberry.type
class VariableStoreState:
    """Represents the state of the AttackMate variable store."""
    # JSON scalar for the  the map[string, Any]
    variables: JSON  # {'var1': 'value', 'list1': ['a', 'b']} etc.


@strawberry.type
class ExecutionResponse:
    """Response containing command result and updated state."""
    result: CommandResult
    state: VariableStoreState


@strawberry.type
class PlaybookExecutionResponse:
    """Response after executing a full playbook."""
    success: bool
    message: str
    final_state: VariableStoreState


# Input Type for Commands
# ALL fields from ALL supported command Pydantic models  Optional

@strawberry.input
class CommandInput:
    """Input for executing a single command."""
    # Common fields (mapping toBaseCommand)
    type: str
    cmd: Optional[str] = None
    only_if: Optional[str] = None
    error_if: Optional[str] = None
    error_if_not: Optional[str] = None
    loop_if: Optional[str] = None
    loop_if_not: Optional[str] = None
    loop_count: Optional[str] = None  # actually StringNumber
    exit_on_error: Optional[bool] = None
    save: Optional[str] = None
    background: Optional[bool] = None
    kill_on_exit: Optional[bool] = None
    metadata: Optional[JSON] = None  # actually dict

    # Specific Fields

    # ShellCommand fields
    interactive: Optional[bool] = None
    creates_session: Optional[str] = None
    session: Optional[str] = None
    command_timeout: Optional[str] = None   # actually StringNumber
    read: Optional[bool] = None
    command_shell: Optional[str] = None
    bin: Optional[bool] = None

    # SleepCommand fields
    min_sec: Optional[str] = None  # actually StringNumber
    seconds: Optional[str] = None   # actually StringNumber
    random: Optional[bool] = None

    # DebugCommand fields
    varstore: Optional[bool] = None
    exit: Optional[bool] = None
    wait_for_key: Optional[bool] = None

    # SetVarCommand fields
    variable: Optional[str] = None
    encoder: Optional[str] = None

    # TempfileCommand (mktemp) fields
    make_dir: Optional[bool] = None  # Use a boolean flag for cmd='dir' ?
    # variable: Optional[str] = None already defined in setvar

# TODO what about variable name conflicts?

# HELPERS


# --- Helper Function ---
def _varstore_to_gql_state(varstore: VariableStore) -> VariableStoreState:
    """Converts AttackMate VariableStore to GraphQL VariableStoreState."""
    combined_vars: Dict[str, Any] = {}
    combined_vars.update(varstore.variables)
    combined_vars.update(varstore.lists)
    return VariableStoreState(variables=combined_vars)  # type: ignore[call-arg]

# RESOLVERS


@strawberry.type
class Query:

    @strawberry.field
    def hello(self) -> str:
        return 'API is running!'

    @strawberry.field
    def get_state(self, info: Info) -> VariableStoreState:
        """Gets the current variable store state from the context."""
        # Access dependencies from context
        attackmate_instance = info.context.get('attackmate_instance')
        if not attackmate_instance:
            raise Exception('AttackMate instance not found')
        logger.info('Query: get_state received.')
        return _varstore_to_gql_state(attackmate_instance.varstore)


# PLAYBOOK EXECUTION
@strawberry.type
class Mutation:
    @strawberry.mutation
    def execute_playbook(self, info: Info, playbook_yaml: str, initial_state: Optional[JSON] = None) -> PlaybookExecutionResponse:
        """Executes an entire playbook provided as YAML."""
        logger.info('Mutation: execute_playbook received.')
        attackmate_config = info.context.get('attackmate_config')
        if not attackmate_config:
            raise Exception('AttackMate config not found in context')
        try:
            playbook_dict = yaml.safe_load(playbook_yaml)
            if not playbook_dict:
                raise ValueError('Empty playbook YAML')
            playbook = Playbook.model_validate(playbook_dict)

            # Prepare initial vars if provided
            initial_vars_dict: Dict[str, Any] = {}
            if initial_state:
                if isinstance(initial_state, dict):
                    initial_vars_dict = initial_state
                else:
                    logger.warning('initial_state was not a valid dictionary, ignoring.')

            # transient AttackMate instance for playbook run
            logger.info('Creating transient AttackMate instance for playbook execution...')
            am_instance = AttackMate(playbook=playbook, config=attackmate_config, varstore=initial_vars_dict)
            logger.info('Transient AttackMate instance created.')

            # Execute the playbook
            return_code = am_instance.main()
            final_varstore = am_instance.varstore
            am_instance.clean_session_stores()
            logger.info(f"Playbook execution finished with code: {return_code}")

            return PlaybookExecutionResponse(
                success=(return_code == 0),
                message='Playbook execution finished.',
                final_state=_varstore_to_gql_state(final_varstore)
            )  # type: ignore[call-arg]

        except (yaml.YAMLError, ValidationError, ValueError) as e:
            logger.error(f"Error processing playbook: {e}", exc_info=True)
            return PlaybookExecutionResponse(success=False, message=f"Playbook Error: {e}", final_state=VariableStoreState(variables={}))  # type: ignore[call-arg]
        except Exception as e:
            logger.error(f"Unexpected error during playbook execution: {e}", exc_info=True)
            return PlaybookExecutionResponse(success=False, message=f"Server Error: {e}", final_state=VariableStoreState(variables={}))  # type: ignore[call-arg]

    @strawberry.mutation
    def execute_remote_playbook(self, info: Info, playbook_file_path: str, initial_state: Optional[JSON] = None) -> PlaybookExecutionResponse:
        """Executes an entire playbook provided as YAML."""
        logger.info('Mutation: execute_remote_playbook received.')
        attackmate_config = info.context.get('attackmate_config')
        if not attackmate_config:
            raise Exception('AttackMate config not found in context')
        try:
            with open(playbook_file_path, 'r') as f:
                playbook_yaml_content = f.read()
        except FileNotFoundError:
            logger.error(f"Error: Playbook file not found at '{playbook_file_path}'")
            sys.exit(1)
        except Exception as e:
            logger.error(f"Error reading playbook file '{playbook_file_path}': {e}")
            sys.exit(1)
        try:
            playbook_dict = yaml.safe_load(playbook_yaml_content)
            if not playbook_dict:
                raise ValueError('Empty playbook YAML')
            playbook = Playbook.model_validate(playbook_dict)
            # Prepare initial vars if provided
            initial_vars_dict: Dict[str, Any] = {}
            if initial_state:
                if isinstance(initial_state, dict):
                    initial_vars_dict = initial_state
                else:
                    logger.warning('initial_state was not a valid dictionary, ignoring.')
            # transient AttackMate instance for playbook run
            logger.info('Creating transient AttackMate instance for playbook execution...')
            am_instance = AttackMate(playbook=playbook, config=attackmate_config, varstore=initial_vars_dict)
            logger.info('Transient AttackMate instance created.')
            # Execute the playbook
            return_code = am_instance.main()
            final_varstore = am_instance.varstore
            am_instance.clean_session_stores()
            logger.info(f"Playbook execution finished with code: {return_code}")
            return PlaybookExecutionResponse(
                success=(return_code == 0),
                message='Playbook execution finished.',
                final_state=_varstore_to_gql_state(final_varstore)
            )  # type: ignore[call-arg]
        except (yaml.YAMLError, ValidationError, ValueError) as e:
            logger.error(f"Error processing playbook: {e}", exc_info=True)
            return PlaybookExecutionResponse(success=False, message=f"Playbook Error: {e}", final_state=VariableStoreState(variables={}))  # type: ignore[call-arg]
        except Exception as e:
            logger.error(f"Unexpected error during playbook execution: {e}", exc_info=True)
            return PlaybookExecutionResponse(success=False, message=f"Server Error: {e}", final_state=VariableStoreState(variables={}))  # type: ignore[call-arg]

# SINGLE COMMAND EXECUTION

    @strawberry.mutation
    def execute_command(self, info: Info, command: CommandInput) -> ExecutionResponse:
        """Executes a single command using the persistent server state."""
        logger.info(f"Mutation: execute_command received for type: {command.type}")
        attackmate_instance = info.context.get('attackmate_instance')
        if not attackmate_instance:
            err_msg = 'AttackMate instance not available in context.'
            logger.error(err_msg)
            return ExecutionResponse(result=CommandResult(success=False, error_message=err_msg, returncode=-1), state=VariableStoreState(variables={}))  # type: ignore[call-arg]
        pydantic_cmd = None

        try:
            # Strawberry Input to Python Dict
            command_dict = {
                k: v for k, v in strawberry.asdict(command).items() if v is not None
            }

            # Handle specific input mappings
            command_type = command_dict.get('type')
            if not command_type:
                raise ValueError("'type' field is required in CommandInput.")

            # Special handling for mktemp (tempfile) type mapping
            if command_type == 'mktemp':
                command_dict['type'] = 'mktemp'
                # Map make_dir flag to Pydantic 'cmd' field for TempfileCommand
                if command_dict.pop('make_dir', False):
                    command_dict['cmd'] = 'dir'
                else:
                    # default is file
                    pass

            # get Pydantic Class via CommandRegistry
            pydantic_type_key = command_dict['type']
            pydantic_cmd_key = command_dict.get('cmd')

            CommandClass = CommandRegistry.get_command_class(pydantic_type_key, pydantic_cmd_key)
            if CommandClass is None and pydantic_cmd_key:  # Try without cmd if specific lookup failed
                CommandClass = CommandRegistry.get_command_class(pydantic_type_key)

            if CommandClass is None:
                raise ValueError(f"Could not find registered Pydantic model for type='{pydantic_type_key}', cmd='{pydantic_cmd_key}'")

            # Validate
            logger.debug(f"Data for Pydantic validation ({CommandClass.__name__}): {command_dict}")
            pydantic_cmd = CommandClass.model_validate(command_dict)
            logger.info(f"Converted input to Pydantic: {type(pydantic_cmd).__name__}")

            # Execute the command
            logger.info('Calling attackmate_instance.run_command')
            attackmate_result = attackmate_instance.run_command(pydantic_cmd)
            logger.info(f"Returned from attackmate_instance.run_command. Result: {attackmate_result!r}")

            # Prepare result
            gql_result = CommandResult(
                 success=True,
                 stdout=str(attackmate_result.stdout) if attackmate_result.stdout is not None else None,
                 returncode=attackmate_result.returncode,
                 error_message=None
            )  # type: ignore[call-arg]
            # Special case for background/skipped commands
            if attackmate_result.stdout is None and attackmate_result.returncode is None:
                gql_result.stdout = 'Command likely backgrounded or skipped.'
                gql_result.returncode = 0

        except (ExecException, SystemExit) as e:
            logger.error(f"AttackMate execution error: {e}", exc_info=True)
            gql_result = CommandResult(
                success=False,
                stdout=None,
                returncode=e.code if isinstance(e, SystemExit) and isinstance(e.code, int) else 1,
                error_message=f"Execution Error: {e}"
            )  # type: ignore[call-arg]
        except (ValidationError, ValueError) as e:
            logger.error(f"Input validation/conversion error: {e}", exc_info=True)
            gql_result = CommandResult(success=False, returncode=-1, error_message=f"Input Error: {e}")  # type: ignore[call-arg]
        except Exception as e:
            logger.error(f"Unexpected server error: {e}", exc_info=True)
            gql_result = CommandResult(success=False, returncode=-1, error_message=f"Server Error: {e}")  # type: ignore[call-arg]

        # Get final state from persistent instance
        final_gql_state = _varstore_to_gql_state(attackmate_instance.varstore)

        return ExecutionResponse(result=gql_result, state=final_gql_state)  # type: ignore[call-arg]


# Pass instances of the resolver classes to Schema
schema = strawberry.Schema(query=Query(), mutation=Mutation())
