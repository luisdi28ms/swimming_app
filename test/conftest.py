import pytest
import os
from main import app, db

@pytest.fixture
def client():
    app.config['TESTING'] = True
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:'
    app.config['UPLOAD_FOLDER'] = '/tmp/test_uploads'
    os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

    with app.test_client() as client:
        with app.app_context():
            db.create_all()
            yield client
            db.drop_all()
