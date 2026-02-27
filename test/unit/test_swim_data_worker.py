import pytest
import pandas as pd
import json
from unittest.mock import MagicMock, patch
from consumers.swim_data_worker import compute_stats, process_file, handle_message

@pytest.fixture
def app_ctx():
    from main import app
    with app.app_context():
        yield app

class TestWorker:

    def test_compute_stats_logic(self):
        """Arrange, Act, Assert for the dataframe math."""
        # Arrange
        data = {
            "sourceName": ["Apple Watch", "Connect IQ"],
            "value": [500, 1000],
            "startDate": ["2026-01-01 08:00:00", "2026-01-01 09:00:00"],
            "endDate": ["2026-01-01 08:30:00", "2026-01-01 09:30:00"]
        }
        df = pd.DataFrame(data)

        # Act
        result = compute_stats(df)

        # Assert
        assert len(result) == 1
        assert result.iloc[0]["Value"] == 1500
        assert result.iloc[0]["Source Name"] == "Apple Watch"
        assert result.iloc[0]["Duration"] == 90.0

    @patch("consumers.swim_data_worker.pd.read_csv")
    @patch("consumers.swim_data_worker.SwimStats")
    @patch("consumers.swim_data_worker.RawSwimmingDistance")
    @patch("consumers.swim_data_worker.db")
    def test_process_file_updates_db(self, mock_db, mock_raw, mock_stats, mock_read, app_ctx):
        """Tests that process_file reads CSV and updates database records."""
        # Arrange
        mock_read.return_value = pd.DataFrame({
            "sourceName": ["Apple"], "value": [100], "unit": ["m"],
            "startDate": ["2026-01-01 10:00:00"], "endDate": ["2026-01-01 10:15:00"]
        })

        existing_stats = MagicMock()
        mock_stats.query.first.return_value = existing_stats

        record = MagicMock()
        record.__dict__ = {"sourceName": "Apple", "value": 100, "startDate": "2026-01-01 10:00:00", "endDate": "2026-01-01 10:15:00"}
        mock_raw.query.all.return_value = [record]

        # Act
        process_file("fake_path.csv", "swimming_distance.csv")

        # Assert
        assert existing_stats.total_distance == 100
        assert mock_db.session.commit.called

    def test_handle_message_success(self):
        """Tests that a valid message is acknowledged (ack)."""
        # Arrange
        ch = MagicMock()
        method = MagicMock(delivery_tag=1)
        body = json.dumps({"filepath": "test.csv", "filename": "swimming_distance.csv"})

        with patch("consumers.swim_data_worker.process_file") as mock_process:
            # Act
            handle_message(ch, method, None, body)

            # Assert
            mock_process.assert_called_once_with("test.csv", "swimming_distance.csv")
            ch.basic_ack.assert_called_with(delivery_tag=1)

    def test_handle_message_error(self):
        """Tests that a failure results in a nack with requeue."""
        # Arrange
        ch = MagicMock()
        method = MagicMock(delivery_tag=1)
        body = json.dumps({"filepath": "bad.csv", "filename": "error.csv"})

        with patch("consumers.swim_data_worker.process_file", side_effect=Exception("Boom!")):
            # Act
            handle_message(ch, method, None, body)

            # Assert
            ch.basic_nack.assert_called_with(delivery_tag=1, requeue=True)

    @patch("consumers.swim_data_worker.pd.read_csv")
    @patch("consumers.swim_data_worker.SwimStats")
    @patch("consumers.swim_data_worker.RawSwimmingDistance")
    @patch("consumers.swim_data_worker.db")
    def test_process_file_creates_new_stats_if_none(self, mock_db, mock_raw, mock_stats_class, mock_read, app_ctx):
        """Tests the branch where SwimStats does not exist yet and must be created."""
        # Arrange

        mock_read.return_value = pd.DataFrame({
            "sourceName": ["Apple"], "value": [100], "unit": ["m"],
            "startDate": ["2026-01-01 10:00:00"], "endDate": ["2026-01-01 10:15:00"]
        })

        mock_stats_class.query.first.return_value = None

        new_stats_instance = MagicMock()
        mock_stats_class.return_value = new_stats_instance

        record = MagicMock()
        record.__dict__ = {"sourceName": "Apple", "value": 100, "startDate": "2026-01-01 10:00:00", "endDate": "2026-01-01 10:15:00"}
        mock_raw.query.all.return_value = [record]

        # Act
        process_file("fake_path.csv", "swimming_distance.csv")

        # Assert

        mock_stats_class.assert_called() 

        mock_db.session.add.assert_called_with(new_stats_instance)

        assert new_stats_instance.total_distance == 100
        assert mock_db.session.commit.called
