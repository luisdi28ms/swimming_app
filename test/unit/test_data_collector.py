import pytest
from unittest.mock import MagicMock, patch
from controllers.data_collector import DataCollector

@pytest.fixture
def app():
    from main import app
    app.config['TESTING'] = True
    app.config['UPLOAD_FOLDER'] = '/tmp/uploads'
    return app

class TestDataCollector:

    def test_collect_user_data_no_file(self, app):
        """Tests the error path using a proper request context."""
        collector = DataCollector()

        with app.test_request_context():

            with patch("controllers.data_collector.request") as mock_req:
                mock_req.files = {}

                # Act
                response, status_code = collector.collect_user_data()

                # Assert
                assert status_code == 400
                assert "Error: No file selected!" in response

    @patch("controllers.data_collector.queue")
    @patch("controllers.data_collector.render_template")
    def test_collect_user_data_success(self, mock_render, mock_queue, app):
        """Tests the success path with a simulated file upload."""
        collector = DataCollector()

        mock_file = MagicMock()
        mock_file.filename = "swimming_data.csv"

        with app.test_request_context(method="POST", data={"user_input": mock_file}):

            with patch("controllers.data_collector.request") as mock_req:
                mock_req.files = {"user_input": mock_file}
                mock_render.return_value = "Success Template"

                # Act
                response = collector.collect_user_data()

                # Assert
                expected_path = "/tmp/uploads/swimming_data.csv"
                mock_file.save.assert_called_once_with(expected_path)
                mock_queue.publish_job.assert_called_once()
                assert response == "Success Template"
