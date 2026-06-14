from fastapi.testclient import TestClient
from backend.main import app
import pytest
from unittest.mock import MagicMock, patch

@pytest.fixture
def client():
    with TestClient(app) as c:
        yield c

def test_get_issue_integration(client):
    """
    Integration test: Create issue -> Get issue
    """
    # Mock file validation and background tasks (AI)
    with patch('backend.main.validate_uploaded_file'), \
         patch('backend.main.BackgroundTasks.add_task'), \
         patch('backend.main.save_file_blocking'): # prevent file IO

        # Create
        response = client.post(
            "/api/issues",
            data={"description": "Integration Test Issue", "category": "road"},
        )
        assert response.status_code == 200
        issue_id = response.json()["id"]

        # Get
        response = client.get(f"/api/issues/{issue_id}")
        assert response.status_code == 200
        data = response.json()
        assert data["id"] == issue_id
        assert data["description"] == "Integration Test Issue"
        assert data["category"] == "road"

def test_get_issue_not_found(client):
    response = client.get("/api/issues/999999")
    assert response.status_code == 404
