from functools import partial

from chalice.test import Client

from chalicelib.db import MemoryPersistence, User
from covibot.app import app
import pytest


@pytest.fixture
def client():
    auser = User(id='1', group=1, username='Manuel')
    db = MemoryPersistence(users={'1': auser})
    with Client(app) as client:
        client._app.db = db
        yield client


post_form = partial(client.http.post, headers={'content-type': 'application/x-www-form-urlencoded'})


def test_only_form_encoded_posts_are_allowed(client):
    response = client.http.post('/reservar')
    assert response.body == b'Only form encoded payloads are allowed.'
    assert response.headers == {'Content-Type': 'application/json'}
    assert response.status_code == 400


def test_commands_accept_form_requests(client):
    response = post_form('/reservar', body='user_id=99&b=2')
    assert response.body == b"Unable to find user with id `'99'`"


def test_commands_accept_form_requests_full(client):
    auser = User(id='1', group=1, username='Manuel')
    db = MemoryPersistence(users={'1': auser})

    client._app.db = db
    response = post_form('/reservar', body='user_id=1')
    assert b'Reserva Realizada' in response.body
