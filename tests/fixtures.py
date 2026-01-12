import os
import pytest
from scotclimpact import create_app
from scotclimpact.data import make_pooch

@pytest.fixture(scope='session')
def test_app():
    '''Test fixture for the Flask app.
    Docs: https://flask.palletsprojects.com/en/stable/testing/
    '''
    app_under_test = create_app()
    app_under_test.config.update({
        "TESTING": True,
    })

    yield app_under_test

@pytest.fixture()
def client(test_app):
    return test_app.test_client()

@pytest.fixture()
def runner(test_app):
    return test_app.test_cli_runner()

POOCH = make_pooch()

@pytest.fixture()
def pooch_fetcher():
    return lambda filename: POOCH.fetch(filename)
