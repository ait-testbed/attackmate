import logging
import os
import datetime
from contextlib import contextmanager
from typing import Generator, List, Optional

# directory for instance logs if running from project root:
LOG_DIR = os.path.join(os.getcwd(), "attackmate_server_logs")
# Or absolute path:
# LOG_DIR = "/var/log/attackmate_instances" # must exists and has write permissions

# List of logger names to add instance-specific handlers to
TARGET_LOGGER_NAMES = ['playbook', 'output']  # json not needed

# Create  formatter for the instance files
instance_log_formatter = logging.Formatter(
    '%(asctime)s %(levelname)s - %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)


@contextmanager
def instance_logging(instance_id: str, log_level: int = logging.INFO):
    """
    Context manager to temporarily add a file handler for a specific instance
    to the target AttackMate loggers.
    """
    handlers: List[logging.FileHandler] = []
    instance_output_log_file = None  # Initialize
    instance_attackmate_log_file = None

    try:
        # log directory exists
        os.makedirs(LOG_DIR, exist_ok=True)

        timestamp = datetime.datetime.now().strftime('%Y%m%d_%H%M%S')
        instance_output_log_file = os.path.join(LOG_DIR, f"{timestamp}_{instance_id}_output.log")
        instance_attackmate_log_file = os.path.join(LOG_DIR, f"{timestamp}_{instance_id}_attackmate.log")

        # instance-specific file handler
        #  'a' to append within the same request if multiple logs occur
        # each request gets a new timestamped file.
        output_file_handler = logging.FileHandler(instance_output_log_file, mode='a')
        output_file_handler.setFormatter(instance_log_formatter)
        output_file_handler.setLevel(log_level)

        attackmate_file_handler = logging.FileHandler(instance_attackmate_log_file, mode='a')
        attackmate_file_handler.setFormatter(instance_log_formatter)
        attackmate_file_handler.setLevel(log_level)

        # Add the handler to the target loggers
        for logger_name in TARGET_LOGGER_NAMES:
            logger = logging.getLogger(logger_name)
            logger.setLevel(log_level)
            if logger_name == 'playbook':
                logger.addHandler(attackmate_file_handler)
                handlers.append(attackmate_file_handler)  # remove later finally
            if logger_name == 'output':
                logger.addHandler(output_file_handler)
                handlers.append(output_file_handler)  # remove later in finally
            logging.info(
                (f"Added instance log handlers for '{instance_id}' to logger '{logger_name}' -> "
                 f"{instance_output_log_file} and {instance_attackmate_log_file}")
            )
        yield [instance_attackmate_log_file, instance_output_log_file]  # 'with' block executes here

    except Exception as e:
        logging.error(f"Error setting up instance logging for '{instance_id}': {e}", exc_info=True)
        yield  # main code execution if logging fails

    finally:
        logging.info(f"Removing instance log handlers for '{instance_id}'...")
        for handler in handlers:
            try:
                for logger_name in TARGET_LOGGER_NAMES:
                    logger = logging.getLogger(logger_name)
                    logger.removeHandler(handler)
                handler.close()
            except Exception as e:
                logging.error(
                    f"Error removing/closing log handler for instance '{instance_id}': {e}", exc_info=True)
        logging.info(f"Instance log handlers removed for '{instance_id}'.")
