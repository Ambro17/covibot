"""
UT For Api Services
"""
import pytest

from chalice.test import Client
from freezegun import freeze_time

from chalicelib.db import MemoryPersistence
from covibot.app import app
from chalicelib.reservas.api import reservar_semana, SolicitudReservaSemanal


@pytest.fixture
def client():
    with Client(app) as client:
        yield client


@freeze_time('2020-01-11')
def test_reservar(client):
    INVALID_GROUP = '3'
    INVALID_USER = '-1'
    testing_db = MemoryPersistence(
        users={
            '1': dict(id='1', username='Someone', group='1'),
            '2': dict(id='2', username='Name', group='2'),
            '3': dict(id='3', username='El', group=INVALID_GROUP),
        },
    )

    assert reservar_semana(testing_db, '1') == SolicitudReservaSemanal(
        ok=True,
        message='✔️ Reserva Realizada',
        days=['L', 'M', 'X'],
    )
    assert reservar_semana(testing_db, '2') == SolicitudReservaSemanal(
        ok=True,
        message='✔️ Reserva Realizada',
        days=['J', 'V'],
    )
    assert reservar_semana(testing_db, INVALID_USER) == SolicitudReservaSemanal(
        ok=False,
        message='❌ Usted no existe 👻',
        days=[],
    )
    assert reservar_semana(testing_db, INVALID_GROUP) == SolicitudReservaSemanal(
        ok=False,
        message="Grupo Inválido: `'3'`",
        days=[],
    )
    assert testing_db.reservas == [
        ('1', [
            '2020-01-13',
            '2020-01-14',
            '2020-01-15',
        ]),
        ('2', [
            '2020-01-16',
            '2020-01-17',
        ]),
    ]