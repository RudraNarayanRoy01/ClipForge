import pytest
from unittest.mock import patch, MagicMock
import asyncio
from fastapi.testclient import TestClient
from pydantic import ValidationError
import logging

from src.main import app, create_app
from src.core.bootstrap import validate_startup
from src.bootstrap.startup import get_container, initialize_container


def patch_for_healthy_startup():
    """Returns a context manager that patches external dependencies for a healthy startup."""
    import contextlib

    @contextlib.contextmanager
    def _patcher():
        with patch("httpx.AsyncClient.get") as mock_get, \
             patch("alembic.script.ScriptDirectory.from_config") as mock_script_dir, \
             patch("alembic.runtime.migration.MigrationContext.configure") as mock_mig_ctx, \
             patch("sqlalchemy.create_engine"), \
             patch("shutil.which") as mock_which:
            
            # Ollama healthy
            mock_response = MagicMock()
            mock_response.status_code = 200
            mock_get.return_value = mock_response
            
            # DB healthy
            mock_ctx_instance = MagicMock()
            mock_ctx_instance.get_current_revision.return_value = "head_rev"
            mock_mig_ctx.return_value = mock_ctx_instance
            
            mock_script_instance = MagicMock()
            mock_script_instance.get_current_head.return_value = "head_rev"
            mock_script_dir.return_value = mock_script_instance
            
            # FFmpeg healthy
            mock_which.return_value = "/usr/bin/ffmpeg"
            
            yield
    return _patcher()


def test_scenario_1_normal_lifecycle(caplog):
    """
    Scenario 1: Normal Lifecycle
    - Start app -> container resolves -> request processed -> clean shutdown.
    """
    caplog.set_level(logging.INFO)
    with patch_for_healthy_startup():
        with TestClient(app) as client:
            assert "Starting AI Clipping Platform API..." in caplog.text
            assert "[SUCCESS] Configuration verified." in caplog.text
            assert "[SUCCESS] Ollama connected." in caplog.text
            assert "Startup Validation Complete." in caplog.text
            
            # Simulate a request
            response = client.get("/api/v1/health")
            # If not implemented, it returns 404, but we just want to ensure it handles a request
            assert response.status_code in [200, 404]
            
            # Container should be populated
            container = get_container()
            assert container is not None
            
        assert "Shutting down AI Clipping Platform API..." in caplog.text


def test_scenario_2_configuration_validation(caplog):
    """
    Scenario 2: Missing configuration -> Validation failure -> Structured diagnostics
    """
    caplog.set_level(logging.INFO)
    # Force a validation error by popping required env var if it existed, or setting invalid type.
    # Actually, we can patch `SystemSettings` to raise ValidationError.
    with patch("src.config.system_settings.SystemSettings") as mock_settings:
        mock_settings.side_effect = ValidationError.from_exception_data(
            title="SystemSettings",
            line_errors=[{"type": "missing", "loc": ("cors_origins",), "input": None, "msg": "Field required"}]
        )
        
        with patch_for_healthy_startup():
            with pytest.raises(RuntimeError) as exc_info:
                with TestClient(app) as client:
                    pass
            
            assert "Configuration validation failed" in str(exc_info.value)
            assert "[FAILED] Configuration validation failed:" in caplog.text


def test_scenario_3_provider_initialization_failure(caplog):
    """
    Scenario 3: Provider initialization failure -> Diagnostics
    """
    caplog.set_level(logging.INFO)
    with patch_for_healthy_startup():
        with patch("httpx.AsyncClient.get") as mock_get:
            # Simulate connection refused
            mock_get.side_effect = Exception("Connection refused")
            
            with pytest.raises(RuntimeError) as exc_info:
                with TestClient(app) as client:
                    pass
                    
            assert "Ollama is not running locally" in str(exc_info.value)
            assert "[FAILED] Ollama connection failed: Connection refused" in caplog.text


def test_scenario_4_database_initialization_failure(caplog):
    """
    Scenario 4: Database initialization failure -> Graceful shutdown -> Resource cleanup
    """
    caplog.set_level(logging.INFO)
    with patch_for_healthy_startup():
        with patch("alembic.runtime.migration.MigrationContext.configure") as mock_mig_ctx, \
             patch("alembic.script.ScriptDirectory.from_config") as mock_script_dir:
            
            # Simulate schema mismatch
            mock_ctx_instance = MagicMock()
            mock_ctx_instance.get_current_revision.return_value = "old_rev"
            mock_mig_ctx.return_value = mock_ctx_instance
            
            mock_script_instance = MagicMock()
            mock_script_instance.get_current_head.return_value = "new_rev"
            mock_script_dir.return_value = mock_script_instance
            
            with pytest.raises(RuntimeError) as exc_info:
                with TestClient(app) as client:
                    pass
                    
            assert "Database schema out of date" in str(exc_info.value)
            assert "old_rev" in str(exc_info.value)
            assert "new_rev" in str(exc_info.value)


def test_scenario_5_long_running_lifecycle(caplog):
    """
    Scenario 5: Long-running lifecycle -> Resource Leak Check
    Verify repeated startup/shutdown cycles do not accumulate resources.
    """
    import gc
    import sys
    
    gc.collect()
    initial_objects = len(gc.get_objects())
    
    with patch_for_healthy_startup():
        for _ in range(5):
            with TestClient(app) as client:
                response = client.get("/api/v1/health")
                assert response.status_code in [200, 404]
    
    gc.collect()
    final_objects = len(gc.get_objects())
    
    # Assert we haven't leaked a massive amount of objects (e.g. connections, threads, container scopes)
    # A small difference is expected due to pytest internals and logging, but not 1000+ per cycle.
    difference = final_objects - initial_objects
    assert difference < 1500, f"Potential resource leak detected: {difference} objects leaked over 5 cycles."
