class StrategyError(Exception):
    """Base exception for all strategy execution failures."""
    pass


class StrategyGenerationError(StrategyError):
    """Raised when strategy generation fails to produce a valid intent."""
    pass
