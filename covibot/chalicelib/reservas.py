from chalicelib.db import get_database


db = get_database()


def reservar(user_id, dia):
    db.reservar(user_id, dia)


def cancelar(user_id, dia):
    db.cancelar_reserva(user_id, dia)


def listar_reservas():
    db.list_reservas()


def admin_delete_reserva(username, dia):
    user = db.get_user_by_username(username)
    db.cancelar_reserva(user.id, dia)
