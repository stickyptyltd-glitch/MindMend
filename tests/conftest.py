import os
import sys
import pytest


# Ensure the MindMend app directory is importable
TESTS_DIR = os.path.dirname(__file__)
APP_DIR = os.path.abspath(os.path.join(TESTS_DIR, ".."))
if APP_DIR not in sys.path:
    sys.path.insert(0, APP_DIR)


@pytest.fixture()
def app():
    from app import app as flask_app
    yield flask_app


@pytest.fixture()
def client(app):
    with app.test_client() as client:
        with app.app_context():
            yield client

