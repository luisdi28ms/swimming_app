import pytest
import unittest.mock
from app import app

@pytest.fixture
def http_client():
    return app.test_client()

def test_main(http_client):
    # Arrange
    # Act
    response = http_client.get("/")
    # Assert
    assert response.status_code == 200

