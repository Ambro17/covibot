"""
Las reservas pueden ser por dia o por grupo de dias.
"""
import datetime as dt
from dataclasses import dataclass
from typing import List

from chalicelib.db import get_database, User, Reserva

db = get_database()


@dataclass
class SolicitudReservaSemanal:
    ok: bool
    data: str


def reservar_semana(db, user: User) -> SolicitudReservaSemanal:
    dias_a_reservar = get_dias_a_reservar(dt.date.today(), user.group)
    datekeys = get_dias_keys(dias_a_reservar)
    reserva = db.reservar_dias(user.username, datekeys)  # TODO: Don't reserve if it's already reserved.
    if not reserva.otorgada:
        print(f'[ERROR] {reserva.mensaje}')
        return SolicitudReservaSemanal(ok=False, data='❌ Hubo un error al intentar realizar la reserva')

    return SolicitudReservaSemanal(ok=True, data=f'✔️ Reserva Realizada para los días:\n `{datekeys}`')


def get_dias_a_reservar(current_date: dt.date, group: int) -> List[dt.date]:
    weekdays_by_group = {
        1: [0, 1, 2], # L M X
        2: [3, 4],    # J V
    }
    weekdays = weekdays_by_group[group]
    current_weekday = current_date.weekday()
    future_weekdays = list(filter(lambda wd: wd >= current_weekday,weekdays))
    if not future_weekdays:
        # If we have passed all group weekdays reserve for next week
        # For example, a thursday on group 1 will reserve all days for the next week
        future_weekdays = weekdays

    future_dates = []
    for fwday in future_weekdays:
        # 3 % 7 = 3; -1 % 7 = 6, six days until day
        days_diff = (fwday - current_weekday) % 7
        future_dates.append(current_date + dt.timedelta(days=days_diff))

    return future_dates


def get_dias_keys(dias):
    return [dia.strftime('%Y-%m-%d') for dia in dias]


@dataclass
class CancelacionReservaSemanal:
    ok: bool
    data: str


def cancelar_reserva_semana(db, user) -> CancelacionReservaSemanal:
    dias_a_cancelar = get_dias_a_reservar(dt.date.today(), user.group)
    datekeys = get_dias_keys(dias_a_cancelar)

    cancelacion = db.cancelar_reserva_dias(datekeys)
    if not cancelacion.cancelada:
        print(f'[ERROR] {cancelacion.mensaje}')
        return CancelacionReservaSemanal(ok=False, data='❌ Error al cancelar reserva')

    return CancelacionReservaSemanal(ok=True, data='✔️ Reserva Cancelada')


def listar_reservas(db) -> List[Reserva]:
    return db.list_reservas()


def admin_delete_reserva(user_id, dia):
    db.cancelar_reserva(user_id, dia)
