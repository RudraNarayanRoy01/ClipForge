import subprocess
import logging
from typing import List, Optional
from src.config.media_settings import MediaSettings
from src.media.exceptions import (
    SubprocessExecutionError,
    MediaProcessingTimeoutError,
    MediaProcessingError
)

logger = logging.getLogger(__name__)

class SubprocessExecutor:
    """Internal execution utility for safely running subprocesses."""

    def __init__(self, settings: MediaSettings):
        self.settings = settings

    def execute_command(self, command: List[str], timeout: Optional[int] = None) -> subprocess.CompletedProcess:
        """
        Executes a subprocess safely with timeouts and exception translation.
        Never uses shell=True. Only accepts argument lists.
        """
        if not isinstance(command, list):
            raise ValueError("Command must be a list of arguments for security reasons (no shell=True).")

        exec_timeout = timeout if timeout is not None else self.settings.process_timeout
        logger.debug(f"Executing subprocess: {command[0]} with timeout {exec_timeout}s")

        try:
            # We never use shell=True for security reasons.
            result = subprocess.run(
                command,
                capture_output=True,
                text=True,
                timeout=exec_timeout,
                check=False
            )
            
            if result.returncode != 0:
                logger.error(f"Subprocess failed with exit code {result.returncode}. Stderr: {result.stderr}")
                raise SubprocessExecutionError(
                    message=f"Command {command[0]} failed.",
                    exit_code=result.returncode,
                    stderr=result.stderr
                )
            
            return result
        except subprocess.TimeoutExpired as e:
            logger.error(f"Subprocess {command[0]} timed out after {exec_timeout} seconds.")
            raise MediaProcessingTimeoutError(f"Process timed out after {exec_timeout}s") from e
        except FileNotFoundError as e:
            logger.error(f"Executable {command[0]} not found.")
            raise MediaProcessingError(f"Executable {command[0]} not found.") from e
        except Exception as e:
            if isinstance(e, (SubprocessExecutionError, MediaProcessingTimeoutError, MediaProcessingError)):
                raise
            logger.error(f"Unexpected error executing subprocess: {str(e)}")
            raise MediaProcessingError(f"Unexpected error executing subprocess: {str(e)}") from e
