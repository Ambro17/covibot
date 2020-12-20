"""
This tests aim to be representative of the production environment.
Mocks, Fakes, etc should be avoided to keep environment
as close to production as possible
"""
import pytest
from chalice.test import Client


@pytest.fixture()
def client():
    from covibot.app import app  # noqa: Delay import so we can patch db. Chalice doesn't support app factory pattern
    with Client(app) as client:
        yield client


def test_reservar():
    pass


def test_cancelar_reserva():
    pass


def test_ver_mis_reservas():
    pass


def test_ver_todas_las_reservas():
    pass


def test_reservar_ver_cancelar_ver_listar_reservas():
    pass
