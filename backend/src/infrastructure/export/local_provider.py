import os
import shutil

from src.domain.services import IExportProvider
from src.domain.models.export import ExportRequest, ExportResult, ExportStatus


class LocalExportProvider(IExportProvider):
    """
    Concrete implementation of IExportProvider using the local filesystem.
    
    Responsible for executing an export by copying the rendered artifact 
    to a requested local destination. Ensures that the source artifact is 
    never deleted or moved, maintaining its lifecycle ownership outside 
    of the export boundary.
    """
    
    def export(self, request: ExportRequest) -> ExportResult:
        """
        Executes a local export by copying the file from source to destination.
        
        Args:
            request: The ExportRequest containing source and destination information.
            
        Returns:
            ExportResult: The domain-specific outcome of the export operation.
            
        Raises:
            FileExistsError: If the destination exists and overwrite_existing is False.
            Exception: Other filesystem infrastructure failures propagate naturally.
        """
        source_path = request.source_media_location
        dest_path = request.settings.destination
        
        if os.path.exists(dest_path) and not request.settings.overwrite_existing:
            raise FileExistsError(
                f"Destination already exists and overwrite is disabled: {dest_path}"
            )
            
        # Create parent directories if they don't exist
        os.makedirs(os.path.dirname(dest_path) or ".", exist_ok=True)
        
        # Copy the file to the destination
        shutil.copy2(source_path, dest_path)
        
        return ExportResult(
            status=ExportStatus.COMPLETED,
            exported_location=dest_path,
            export_metadata={
                "provider": "LocalExportProvider",
                "copied_bytes": os.path.getsize(dest_path)
            }
        )
