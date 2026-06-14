import os
import sys
import pytest
from PIL import Image
import io

# Add the parent directory to sys.path so we can import backend modules if needed
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Assumes backend is running on localhost:8000
API_URL = "http://localhost:8000"

def test_playground_endpoint_structure():
    """
    Since we cannot easily mock the external HF API in a live integration test without
    mocking the whole server or dependencies, and we don't want to rely on the actual
    HF API being up and responsive for a quick verification, we will simulate
    the request using a mocked client if we were unit testing.

    However, for a "live" test against the running backend (if it were running),
    we would do:

    files = {'image': open('dummy.jpg', 'rb')}
    response = requests.post(f"{API_URL}/api/detect-playground", files=files)

    Here, we will create a unit test that imports the router and mocks the HF service.
    """
    pass

# We will use the TestClient from fastapi.testclient to test the app directly
from fastapi.testclient import TestClient
from backend.main import app
from unittest.mock import patch, AsyncMock

@pytest.fixture
def client():
    with TestClient(app) as client:
        yield client

@patch('backend.routers.detection.detect_playground_damage_clip', new_callable=AsyncMock)
def test_detect_playground_api(mock_detect, client):
    # Mock the return value of the service function
    mock_detect.return_value = [
        {"label": "damaged playground equipment", "confidence": 0.95, "box": []},
        {"label": "unsafe slide", "confidence": 0.85, "box": []}
    ]

    # Create a dummy image
    img = Image.new('RGB', (100, 100), color = 'red')
    img_byte_arr = io.BytesIO()
    img.save(img_byte_arr, format='JPEG')
    img_byte_arr.seek(0)

    response = client.post(
        "/api/detect-playground",
        files={"image": ("test.jpg", img_byte_arr, "image/jpeg")}
    )

    assert response.status_code == 200
    data = response.json()
    assert "detections" in data
    assert len(data["detections"]) == 2
    assert data["detections"][0]["label"] == "damaged playground equipment"

    # Verify the service was called
    mock_detect.assert_called_once()
