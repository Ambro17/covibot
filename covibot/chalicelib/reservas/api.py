"""
Las reservas pueden ser por dia o por grupo de dias.
"""
import datetime as dt
from dataclasses import dataclass
from typing import Literal

from chalicelib.db import get_database, SolicitudReserva


db = get_database()


RESERVA_TO_DIA = {
    'G1': 'LMX'.split(),
    'G2': 'JV'.split(),
}

NAME_TO_WEEKDAY = {
    'L': 0,
    'M': 1,
    'X': 2,
    'J': 3,
    'V': 4,
    'S': 5,
    'D': 6,
}
WEEKDAY_TO_NAME = {v: k for k, v in NAME_TO_WEEKDAY.items()}

DIA = Literal['L', 'M', 'X', 'J', 'V']


def reservar_dia(user_id: str, dia: DIA) -> SolicitudReserva:
    dia = dia.upper()
    if dia not in 'LMXJV'.split():
        return SolicitudReserva(otorgada=False, mensaje='El día debe ser uno de `L M X J V`')

    reserva_date = get_reserva_from_day(dia)
    date_key = reserva_date.strftime('%Y-%m-%d')

    reserva = db.reservar_dia(user_id, date_key)

    return reserva


@dataclass
class SolicitudReservaSemanal:
    ok: bool
    message: str


def reservar_semana(user_id: str) -> SolicitudReservaSemanal:
    user = db.get_user(user_id)
    group = user.get('group')
    if not group:
        return SolicitudReservaSemanal(ok=False, message='No tiene grupo asignado aún')

    days_per_group = {
        '1': ['L', 'M', 'X'],
        '2': ['J', 'V'],
    }
    days = days_per_group[group]

    datekeys = get_date_keys(days)

    for day in days:
        date_key = get_date_keys(day)
        reserva = db.reservar_dia(user_id, date_key)
        print('Reserva: ', reserva)

    return SolicitudReservaSemanal(ok=True, message='✔️ Reserva Realizada')


def get_date_keys(day):
    reserva_date = get_reserva_from_day(day)
    date_key = reserva_date.strftime('%Y-%m-%d')
    return date_key


def get_reserva_from_day(dia):
    # If reserva is for monday, get the isodate of next monday and use it as the key
    reserva_weekday: int = NAME_TO_WEEKDAY[dia]
    today = dt.datetime.today() # TODO: Localize to BsAs
    return day_gap(today, reserva_weekday)


def day_gap(date, day: int):
    days_gap = (day - date.weekday()) % 7
    return date + dt.timedelta(days=days_gap)


def cancelar(user_id, dia):
    # First validate the reserva is for her/himself
    ok = db.cancelar_reserva(user_id, dia)


def listar_reservas():
    db.list_reservas()


def admin_delete_reserva(user_id, dia):
    db.cancelar_reserva(user_id, dia)
