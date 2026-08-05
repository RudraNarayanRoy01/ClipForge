from dataclasses import dataclass


@dataclass
class BootstrapConfiguration:
    """
    Configuration exclusively for the Runtime Bootstrap lifecycle.
    
    Contains settings for timeout, diagnostics, validation, and logging.
    This MUST NOT contain AI, provider, or model configuration.
    """
    startup_timeout: float = 30.0
    diagnostics_enabled: bool = False
    validation_enabled: bool = True
    startup_logging: bool = True
    strict_bootstrap_mode: bool = True
