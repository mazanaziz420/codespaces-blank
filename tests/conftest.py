import pytest
from app import app as flask_app

@pytest.fixture(scope='module')
def app():
    flask_app.config['TESTING'] = True
    flask_app.config['MONGO_URI'] = 'mongodb://localhost:27017/test_db'  # Use a test database
    return flask_app

@pytest.fixture(scope='module')
def client(app):
    return app.test_client()

@pytest.fixture(scope='module')
def init_database(app):
    # Initialize database connection or setup if needed
    with app.app_context():
        # Setup or reset the database before tests
        pass
    yield
    with app.app_context():
        # Cleanup the database after tests
        pass
