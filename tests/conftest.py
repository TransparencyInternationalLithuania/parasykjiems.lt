import pytest


@pytest.fixture()
def app(db):
    from django.test.client import Client

    return Client(
        HTTP_HOST='locahost',
    )
