import pytest
from unittest.mock import patch
from main import app

@pytest.fixture
def client():
    app.config['TESTING'] = True
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:'
    with app.test_client() as client:
        with app.app_context():
            yield client

class TestMainRoutes:

    def test_main_route(self, client):
        """Test the home page renders the upload template."""
        # Act
        response = client.get("/")

        # Assert
        assert response.status_code == 200

        assert b"html" in response.data 

    @patch("main.data_collector.collect_user_data")
    def test_collect_data_route(self, mock_collect, client):
        """Test the POST route for data collection."""
        # Arrange
        mock_collect.return_value = "Success"

        # Act
        response = client.post("/collect_user_data")

        # Assert
        assert response.status_code == 200
        assert response.data == b"Success"
        mock_collect.assert_called_once()

    @patch("main.analyzer.render_swimming_report")
    def test_swimming_report_route(self, mock_render, client):
        """Test the report route calls the analyzer."""
        # Arrange
        mock_render.return_value = "Report Content"

        # Act
        response = client.get("/analyze_user_data")

        # Assert
        assert response.status_code == 200
        assert response.data == b"Report Content"
        mock_render.assert_called_once()

    def test_health_check(self, client):
        """Test the health endpoint returns JSON."""
        # Act
        response = client.get("/health")

        # Assert
        assert response.status_code == 200
        assert response.json == {"status": "ok"}

    def test_metrics_endpoint(self, client):
        """Test that prometheus metrics are being served."""
        # Act
        response = client.get("/metrics")

        # Assert
        assert response.status_code == 200
        assert response.mimetype == 'text/plain'

        assert b"http_requests_total" in response.data
