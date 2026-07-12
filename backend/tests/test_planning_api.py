import pytest
import uuid
from fastapi.testclient import TestClient

from src.main import app

client = TestClient(app)

def test_planning_get_404():
    """Verify that getting a non-existent plan returns 404."""
    campaign_id = str(uuid.uuid4())
    response = client.get(f"/api/v1/campaigns/{campaign_id}/plan")
    assert response.status_code == 404

def test_planning_history_empty():
    """Verify that history for a new campaign is empty."""
    campaign_id = str(uuid.uuid4())
    response = client.get(f"/api/v1/planning/history?campaign_id={campaign_id}")
    assert response.status_code == 200
    data = response.json()
    assert "data" in data
    assert len(data["data"]) == 0

def test_planning_post_missing_campaign():
    """Verify that posting to a missing campaign returns 500 (or handles cleanly)."""
    campaign_id = str(uuid.uuid4())
    response = client.post(f"/api/v1/campaigns/{campaign_id}/plan", json={"force_regenerate": False})
    # Since the campaign doesn't exist, PlanningError is raised, wrapped in 500 by controller.
    assert response.status_code == 500
