import pytest
import flask
from app import app as flask_app

@pytest.fixture
def app():
    flask_app.config['TESTING'] = True
    flask_app.config['WTF_CSRF_ENABLED'] = False
    return flask_app

@pytest.fixture
def client(app):
    return app.test_client()

@pytest.fixture
def mock_session(monkeypatch):
    session_data = {}
    monkeypatch.setattr(flask, "session", session_data)
    return session_data

@pytest.fixture
def client():
    with flask_app.test_client() as client:
        yield client


# RUN ALL TESTS  

#   PYTHONPATH=. pytest
