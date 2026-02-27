import pytest
from unittest.mock import patch
from io import BytesIO
from main import app, db
from models.swim_stats import SwimStats
from models.raw_swimming_distance import RawSwimmingDistance
from consumers.swim_data_worker import process_file
import pandas as pd

@pytest.fixture
def integration_client():
    app.config['TESTING'] = True
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:'
    app.config['UPLOAD_FOLDER'] = '/tmp/integration_uploads'

    with app.test_client() as client:
        with app.app_context():
            db.create_all()
            yield client
            db.session.remove()
            db.drop_all()

@patch("controllers.data_collector.queue.publish_job")
@patch("consumers.swim_data_worker.pd.read_csv")
def test_full_flow_upload_to_stats(mock_read_csv, mock_publish, integration_client):
    # --- STEP 1: The Upload ---
    csv_content = b"sourceName,value,unit,startDate,endDate\nApple,500,m,2026-01-01 08:00:00,2026-01-01 08:30:00"

    with patch("controllers.data_collector.os.makedirs"), \
         patch("werkzeug.datastructures.FileStorage.save"):

        data = {
            'user_input': (BytesIO(csv_content), 'swimming_distance.csv')
        }

        response = integration_client.post(
            "/collect_user_data", 
            data=data, 
            content_type='multipart/form-data'
        )

    # Assert
    assert response.status_code == 200
    mock_publish.assert_called_once()

   # --- STEP 2: The Worker Processing ---

    job_data = mock_publish.call_args[0][0]

    mock_read_csv.return_value = pd.DataFrame({
        "sourceName": ["Apple"],
        "value": [500],
        "unit": ["m"],
        "startDate": ["2026-01-01 08:00:00"],
        "endDate": ["2026-01-01 08:30:00"]
    })

    process_file(job_data['filepath'], job_data['filename'])    

    # --- STEP 3: Verify record written to DB ---
    with app.app_context():
        stats = SwimStats.query.first()
        assert stats is not None
        assert stats.total_distance == 500

        raw = RawSwimmingDistance.query.first()
        assert raw.sourceName == "Apple" 
