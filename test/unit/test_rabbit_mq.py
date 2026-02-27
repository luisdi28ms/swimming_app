import pytest
import json
from unittest.mock import MagicMock, patch
from repositories.rabbit_mq import RabbitMQQueue

class TestRabbitMQQueue:

    @patch("repositories.rabbit_mq.pika.BlockingConnection")
    @patch("repositories.rabbit_mq.os.getenv")
    def test_publish_job_success(self, mock_getenv, mock_pika_connection):
        """Test the full flow of connecting and publishing a message."""
        # Arrange
        mock_getenv.return_value = "amqp://guest:guest@localhost:5672/"

        mock_conn = MagicMock()
        mock_channel = MagicMock()
        mock_pika_connection.return_value = mock_conn
        mock_conn.channel.return_value = mock_channel

        queue_service = RabbitMQQueue()
        test_data = {"filepath": "/tmp/test.csv", "filename": "test.csv"}

        # Act
        queue_service.publish_job(test_data)

        # Assert
        mock_pika_connection.assert_called_once()

        mock_channel.queue_declare.assert_called_once_with(
            queue='csv_processing', durable=True
        )

        args, kwargs = mock_channel.basic_publish.call_args
        assert kwargs['routing_key'] == 'csv_processing'
        assert kwargs['body'] == json.dumps(test_data)
        assert kwargs['properties'].delivery_mode == 2

        mock_conn.close.assert_called_once()

    @patch("repositories.rabbit_mq.pika.BlockingConnection")
    def test_publish_job_connection_error(self, mock_pika_connection):
        """Test how the class behaves when RabbitMQ is down."""
        # Arrange
        mock_pika_connection.side_effect = Exception("Connection Refused")
        queue_service = RabbitMQQueue()

        # Act
        with pytest.raises(Exception) as excinfo:
            queue_service.publish_job({"data": "test"})

        # Assert
        assert "Connection Refused" in str(excinfo.value)
