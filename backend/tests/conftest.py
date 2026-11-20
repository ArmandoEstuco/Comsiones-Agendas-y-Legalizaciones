import pytest

from app import create_app


class TestConfig:
    TESTING = True
    JWT_SECRET_KEY = "test-secret-key-with-at-least-32-characters"
    FIRMAS_UPLOAD_FOLDER = ""
    MAX_SIGNATURE_SIZE = 1_048_576
    MAX_CONTENT_LENGTH = 1_048_576


@pytest.fixture
def app():
    return create_app(TestConfig)


@pytest.fixture
def client(app):
    return app.test_client()
