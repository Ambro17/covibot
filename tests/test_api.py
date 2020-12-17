"""
UT For Api Services
"""
import pytest
from freezegun import freeze_time

from chalicelib.db import MemoryPersistence, Reserva, User
from chalicelib.reservas.api import (
    reservar_semana,
    SolicitudReservaSemanal,
    cancelar_reserva_semana,
    CancelacionReservaSemanal, listar_reservas,
)


@freeze_time('2020-01-11')
def test_reservar():
    INVALID_GROUP = 3
    someone = User(id='1', username='Someone', group=1)
    otherone = User(id='2', username='Otherone', group=2)
    badgroupuser = User(id='3', username='Lastone', group=INVALID_GROUP)
    testing_db = MemoryPersistence(
        users={
            '1': someone,
            '2': otherone,
            '3': badgroupuser,
        },
    )

    assert reservar_semana(testing_db, someone) == SolicitudReservaSemanal(
        ok=True,
        data="✔️ Reserva Realizada para los días:\n `['2020-01-13', '2020-01-14', '2020-01-15']`",
    )
    assert reservar_semana(testing_db, otherone) == SolicitudReservaSemanal(
        ok=True,
        data="✔️ Reserva Realizada para los días:\n `['2020-01-16', '2020-01-17']`",
    )
    with pytest.raises(KeyError, match='3'):
        assert reservar_semana(testing_db, badgroupuser) == SolicitudReservaSemanal(
            ok=False,
            data='',
        )
    assert testing_db.reservas == [
        Reserva('Someone', '2020-01-13'),
        Reserva('Someone', '2020-01-14'),
        Reserva('Someone', '2020-01-15'),
        Reserva('Otherone', '2020-01-16'),
        Reserva('Otherone', '2020-01-17'),
    ]


@freeze_time('2020-02-18')
def test_list_reservas():
    auser = User(id='1', username='Golliat', group=1)
    buser = User(id='2', username='Someone', group=2)
    testing_db = MemoryPersistence(
        users={
            '1': auser,
            '2': buser,
        },
    )

    assert reservar_semana(testing_db, buser) == SolicitudReservaSemanal(
        ok=True,
        data="✔️ Reserva Realizada para los días:\n `['2020-02-20', '2020-02-21']`",
    )
    assert reservar_semana(testing_db, auser) == SolicitudReservaSemanal(
        ok=True,
        data="✔️ Reserva Realizada para los días:\n `['2020-02-18', '2020-02-19']`",
    )
    assert listar_reservas(testing_db) == [
        Reserva(name='Someone', dia='2020-02-20'),
        Reserva(name='Someone', dia='2020-02-21'),
        Reserva(name='Golliat', dia='2020-02-18'),
        Reserva(name='Golliat', dia='2020-02-19'),
    ]


def test_reserve_twice_on_different_days():
    auser = User(id='1', username='Golliat', group=1)
    db = MemoryPersistence(
        users={
            '1': auser
        },
    )
    with freeze_time("2020-02-18"):
        assert reservar_semana(db, auser) == SolicitudReservaSemanal(
            ok=True,
            data="✔️ Reserva Realizada para los días:\n `['2020-02-18', '2020-02-19']`",
        )
        assert listar_reservas(db) == [
            Reserva('Golliat', '2020-02-18'),
            Reserva('Golliat', '2020-02-19'),
        ]

    with freeze_time("2020-02-23"):
        assert reservar_semana(db, auser) == SolicitudReservaSemanal(
            ok=True,
            data="✔️ Reserva Realizada para los días:\n `['2020-02-24', '2020-02-25', '2020-02-26']`",
        )

    assert listar_reservas(db) == [
        Reserva('Golliat', '2020-02-18'),
        Reserva('Golliat', '2020-02-19'),
        Reserva('Golliat', '2020-02-24'),
        Reserva('Golliat', '2020-02-25'),  # Added later
        Reserva('Golliat', '2020-02-26'),  # Added later
    ]


def test_cancelacion_removes_reserva():
    auser = User(id='1', username='Someone', group=2)
    db = MemoryPersistence(
        users={
            '1': auser,
        },
    )

    assert reservar_semana(db, auser) == SolicitudReservaSemanal(
        ok=True,
        data="✔️ Reserva Realizada para los días:\n `['2020-12-17', '2020-12-18']`",
    )
    assert len(listar_reservas(db)) == 2
    assert cancelar_reserva_semana(db, auser) == CancelacionReservaSemanal(
        ok=True,
        data='✔️ Reserva Cancelada',
    )
    assert len(listar_reservas(db)) == 0
