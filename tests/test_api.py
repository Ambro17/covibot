"""
UT For Api Services
"""
from freezegun import freeze_time

from chalicelib.db import MemoryPersistence, Reserva
from chalicelib.reservas.api import (
    reservar_semana,
    SolicitudReservaSemanal,
    listar_reservas,
    cancelar_reserva_semana,
    CancelacionReservaSemanal,
)


@freeze_time('2020-01-11')
def test_reservar():
    INVALID_GROUP = '3'
    INVALID_USER = '-1'
    testing_db = MemoryPersistence(
        users={
            '1': dict(id='1', username='Someone', group='1'),
            '2': dict(id='2', username='Otherone', group='2'),
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
        Reserva('Someone', '2020-01-13'),
        Reserva('Someone', '2020-01-14'),
        Reserva('Someone', '2020-01-15'),
        Reserva('Otherone', '2020-01-16'),
        Reserva('Otherone', '2020-01-17'),
    ]


@freeze_time('2020-02-18')
def test_list_reservas():
    testing_db = MemoryPersistence(
        users={
            '1': dict(id='1', username='Golliat', group='1'),
            '2': dict(id='2', username='Someone', group='2'),
        },
    )

    assert reservar_semana(testing_db, '2') == SolicitudReservaSemanal(
        ok=True,
        message='✔️ Reserva Realizada',
        days=['J', 'V'],
    )
    assert reservar_semana(testing_db, '1') == SolicitudReservaSemanal(
        ok=True,
        message='✔️ Reserva Realizada',
        days=['L', 'M', 'X'],
    )
    assert listar_reservas(testing_db) == [
        Reserva(name='Someone', dia='2020-02-20'),
        Reserva(name='Someone', dia='2020-02-21'),
        Reserva(name='Golliat', dia='2020-02-24'),  # Next week
        Reserva(name='Golliat', dia='2020-02-18'),
        Reserva(name='Golliat', dia='2020-02-19'),
    ]


def test_reserve_twice_on_different_days():
    db = MemoryPersistence(
        users={
            '1': dict(id='1', username='Golliat', group='1'),
        },
    )
    with freeze_time("2020-02-18"):
        assert reservar_semana(db, '1') == SolicitudReservaSemanal(
            ok=True,
            message='✔️ Reserva Realizada',
            days=['L', 'M', 'X'],
        )
        assert listar_reservas(db) == [
            Reserva('Golliat', '2020-02-24'),
            Reserva('Golliat', '2020-02-18'),
            Reserva('Golliat', '2020-02-19'),
        ]

    with freeze_time("2020-02-23"):
        assert reservar_semana(db, '1') == SolicitudReservaSemanal(
            ok=True,
            message='✔️ Reserva Realizada',
            days=['L', 'M', 'X'],
        )

    assert listar_reservas(db) == [
        Reserva('Golliat', '2020-02-24'),
        Reserva('Golliat', '2020-02-18'),
        Reserva('Golliat', '2020-02-19'),
        Reserva('Golliat', '2020-02-25'),  # Added later
        Reserva('Golliat', '2020-02-26'),  # Added later
    ]


def test_cancelacion_removes_reserva():
    db = MemoryPersistence(
        users={
            '1': dict(id='1', username='Someone', group='2'),
        },
    )

    assert reservar_semana(db, '1') == SolicitudReservaSemanal(
        ok=True,
        message='✔️ Reserva Realizada',
        days=['J', 'V'],
    )
    assert len(listar_reservas(db)) == 2
    assert cancelar_reserva_semana(db, '1') == CancelacionReservaSemanal(
        ok=True,
        data='✔️ Reserva Cancelada',
    )
    assert len(listar_reservas(db)) == 0
