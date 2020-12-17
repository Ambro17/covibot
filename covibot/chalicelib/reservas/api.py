"""
Las reservas pueden ser por dia o por grupo de dias.
"""
import datetime as dt
from dataclasses import dataclass, field
from typing import Literal, List, Any

from chalicelib.db import get_database, SolicitudReserva, Reserva


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


def reservar_dia(db, user_id: str, dia: DIA) -> SolicitudReserva:
    dia = dia.upper()
    if dia not in 'LMXJV':
        return SolicitudReserva(otorgada=False, mensaje=f'El día debe ser uno de `L M X J V`. No {dia}')

    reserva_date = get_reserva_from_day(dia)
    date_key = reserva_date.strftime('%Y-%m-%d')

    reserva = db.reservar_dia(user_id, date_key)

    return reserva


@dataclass
class SolicitudReservaSemanal:
    ok: bool
    message: str
    days: List[str] = field(default_factory=list)


def reservar_semana(db, user_id: str) -> SolicitudReservaSemanal:
    user = db.get_user(user_id)
    if not user:
        return SolicitudReservaSemanal(ok=False, message='❌ Usted no existe 👻')

    days_per_group = {
        1: ['L', 'M', 'X'],
        2: ['J', 'V'],
    }
    days = days_per_group.get(user.group)
    if not days:
        return SolicitudReservaSemanal(ok=False, message=f'Grupo Inválido: `{user.group!r}`')

    datekeys = get_date_keys(days)
    reserva = db.reservar_dias(user.username, datekeys)  # TODO: Don't reserve if it's already reserved.
    if reserva.otorgada:
        return SolicitudReservaSemanal(ok=True, message='✔️ Reserva Realizada', days=days)
    else:
        print(f'[ERROR] {reserva.mensaje}')
        return SolicitudReservaSemanal(ok=False, message='❌ Hubo un error a realizar la reserva')


def get_date_keys(days: List[str]):
    """Given a list of human days (L M X) returns a str representing the date of the next day"""
    dates = []
    for day in days:
        reserva_date = get_reserva_from_day(day)
        date_key = reserva_date.strftime('%Y-%m-%d')
        dates.append(date_key)

    return dates


def get_reserva_from_day(dia) -> dt.datetime:
    # If reserva is for monday, get the isodate of next monday and use it as the key
    reserva_weekday: int = NAME_TO_WEEKDAY[dia]
    today = dt.datetime.today() # TODO: Localize to BsAs
    days_until_reserva = (reserva_weekday - today.weekday()) % 7
    return today + dt.timedelta(days=days_until_reserva)


@dataclass
class CancelacionReservaSemanal:
    ok: bool
    data: str


def cancelar_reserva_semana(db, user_id) -> CancelacionReservaSemanal:
    # First validate the reserva is for her/himself
    user = db.get_user(user_id)
    if not user:
        return CancelacionReservaSemanal(ok=False, data='❌ Usted no existe 👻')

    resp = get_days_from_user_group(user.group)
    if not resp.ok:
        return CancelacionReservaSemanal(ok=False, data='❌ Usted no pertenece a ningún grupo')

    dias = resp.data
    datekeys = get_date_keys(dias)
    cancelacion = db.cancelar_reserva_dias(datekeys)
    if not cancelacion.cancelada:
        return CancelacionReservaSemanal(ok=False, data='❌ Error al cancelar reserva')

    return CancelacionReservaSemanal(ok=True, data='✔️ Reserva Cancelada')


@dataclass
class Check:
    ok: bool
    data: Any


def get_days_from_user_group(user_group) -> Check:
    days_per_group = {
        '1': ['L', 'M', 'X'],
        '2': ['J', 'V'],
    }
    days = days_per_group.get(user_group)
    if not days:
        return Check(ok=False, data=[])
    else:
        return Check(ok=True, data=days)


def listar_reservas(db) -> List[Reserva]:
    return db.list_reservas()


def admin_delete_reserva(user_id, dia):
    db.cancelar_reserva(user_id, dia)
