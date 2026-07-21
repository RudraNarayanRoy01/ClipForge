import pytest
from pathlib import Path
from src.domain.models.export import ExportRequest, ExportSettings, ExportStatus
from src.infrastructure.export.local_provider import LocalExportProvider

def test_local_export_copies_file_successfully(tmp_path: Path):
    source_dir = tmp_path / "source"
    dest_dir = tmp_path / "dest"
    source_dir.mkdir()
    
    source_file = source_dir / "rendered.mp4"
    source_file.write_text("dummy video content")
    
    dest_file = dest_dir / "output.mp4"
    
    request = ExportRequest(
        source_media_location=str(source_file),
        settings=ExportSettings(
            destination=str(dest_file),
            overwrite_existing=False
        )
    )
    
    provider = LocalExportProvider()
    result = provider.export(request)
    
    assert result.status == ExportStatus.COMPLETED
    assert result.exported_location == str(dest_file)
    assert result.export_metadata["provider"] == "LocalExportProvider"
    
    # Verify destination file exists and has correct content
    assert dest_file.exists()
    assert dest_file.read_text() == "dummy video content"
    
    # Verify source file was NOT moved or deleted (it must be copied)
    assert source_file.exists()


def test_local_export_raises_file_not_found_for_missing_source(tmp_path: Path):
    missing_source = tmp_path / "missing.mp4"
    dest_file = tmp_path / "dest" / "output.mp4"
    
    request = ExportRequest(
        source_media_location=str(missing_source),
        settings=ExportSettings(
            destination=str(dest_file),
            overwrite_existing=False
        )
    )
    
    provider = LocalExportProvider()
    with pytest.raises(FileNotFoundError):
        provider.export(request)


def test_local_export_raises_oserror_if_source_is_dir(tmp_path: Path):
    source_dir = tmp_path / "source_dir"
    source_dir.mkdir()
    dest_file = tmp_path / "dest" / "output.mp4"
    
    request = ExportRequest(
        source_media_location=str(source_dir),
        settings=ExportSettings(
            destination=str(dest_file),
            overwrite_existing=False
        )
    )
    
    provider = LocalExportProvider()
    with pytest.raises(OSError):
        provider.export(request)


def test_local_export_handles_overwrite_flag(tmp_path: Path):
    source_file = tmp_path / "rendered.mp4"
    source_file.write_text("new content")
    
    dest_file = tmp_path / "output.mp4"
    dest_file.write_text("old content")
    
    # Test overwrite = False
    request_no_overwrite = ExportRequest(
        source_media_location=str(source_file),
        settings=ExportSettings(
            destination=str(dest_file),
            overwrite_existing=False
        )
    )
    
    provider = LocalExportProvider()
    with pytest.raises(FileExistsError):
        provider.export(request_no_overwrite)
        
    # Verify content hasn't changed
    assert dest_file.read_text() == "old content"
    
    # Test overwrite = True
    request_overwrite = ExportRequest(
        source_media_location=str(source_file),
        settings=ExportSettings(
            destination=str(dest_file),
            overwrite_existing=True
        )
    )
    
    result = provider.export(request_overwrite)
    assert result.status == ExportStatus.COMPLETED
    assert dest_file.read_text() == "new content"
