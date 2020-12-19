"""
E2E Tests using chalice Testing App.
HTTP Calls replicating slack requests
"""
from chalice.test import Client

from covibot.app import app
import pytest


@pytest.fixture
def client():
    with Client(app) as client:
        yield client


def test_index(client):
    response = client.http.get('/')
    assert response.json_body == {'success': True}


def test_reservar_invalid_day(client):
    pass


def test_reservar_limit_exceeded(client):
    pass


def test_listar_reservas():
    pass


def test_admin_can_delete_reserva():
    pass


def test_admin_can_reserve_for_another_one():
    pass
