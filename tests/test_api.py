"""
UT For Api Services
"""
import pytest

from chalice.test import Client

from covibot.app import app
from chalicelib.db import SolicitudReserva
from chalicelib.reservas.api import reservar_dia


@pytest.fixture
def client():
    with Client(app) as client:
        yield client


def test_reservar(client):
    assert reservar_dia('1', 'L').otorgada is True
    assert reservar_dia('1', 'M').otorgada is True
    assert reservar_dia('1', 'X').otorgada is True
    assert reservar_dia('1', 'J').otorgada is True
    assert reservar_dia('1', 'V').otorgada is True

    assert reservar_dia('1', 'S').otorgada is False
    assert reservar_dia('1', 'S').mensaje is 'Sólo se puede reservar días laborales'
    assert reservar_dia('1', 'D').otorgada is False
    assert reservar_dia('1', 'D').mensaje is 'Sólo se puede reservar días laborales'

    assert reservar_dia('1', 'W') == SolicitudReserva(
        otorgada=False,
        mensaje='`W` no es un día válido. Los días son `L M X J V`'
    )
    assert reservar_dia('1', 'L W') == SolicitudReserva(
        otorgada=False,
        mensaje='`L W` no es un día válido. Los días son `L M X J V`'
    )
    assert reservar_dia('1', 'L 0') == SolicitudReserva(
        otorgada=False,
        mensaje='`L 0` no es un día válido. Los días son `L M X J V`'
    )
    # When a user invokes /reservar
    # Then it does the booking
    # And it notifies the user
    pass