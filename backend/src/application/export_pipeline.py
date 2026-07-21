from src.domain.services import IExportProvider
from src.domain.models.export import ExportRequest, ExportResult


class ExportPipeline:
    """
    Coordinates export requests for ClipForge.
    
    Acts purely as an orchestration layer between callers and export providers.
    It receives export requests, delegates the actual export to a technology-agnostic 
    provider, and returns the domain result, maintaining strict separation of concerns.
    """

    def __init__(self, provider: IExportProvider):
        """
        Initializes the ExportPipeline with a specific export provider.
        
        Args:
            provider: The technology-agnostic export provider to delegate export to.
        """
        self._provider = provider

    def execute(self, request: ExportRequest) -> ExportResult:
        """
        Coordinates a single export request.
        
        Delegates the execution to the underlying export provider, without introducing
        additional error handling, retry logic, or alternative providers.
        
        Args:
            request: The complete configuration and source details for the export.
            
        Returns:
            ExportResult: The outcome of the export request.
            
        Raises:
            Exception: Any exception raised by the provider propagates naturally.
        """
        return self._provider.export(request)
