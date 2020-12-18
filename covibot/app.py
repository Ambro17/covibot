from collections import defaultdict
from functools import partial

from chalice import Chalice, Response
from slack_sdk import WebClient as Slack

from chalicelib.bus import SQSBus
from chalicelib.config import config, Config
from chalicelib.middlewares import (
    validate_request_comes_from_slack,
    log_all_traffic,
    add_user_to_context,
)
from chalicelib.db import get_database
from chalicelib.reservas.api import reservar_semana, cancelar_reserva_semana, listar_reservas, listar_mis_reservas


def init_app(config: Config):
    app = Chalice(app_name="covibot-api")
    app.log.setLevel(config.log_level)

    # Middlewares
    app.register_middleware(validate_request_comes_from_slack, 'http')
    app.register_middleware(add_user_to_context, 'http')
    app.register_middleware(log_all_traffic, 'all')

    app.db = get_database()
    app.bus = SQSBus(queue=config.sqs_url, name=config.sqs_queue_name)
    app.slack = Slack(token=config.slack_bot_token)

    return app


app = init_app(config)

JSONResponse = partial(Response, headers={'Content-Type': 'application/json'})
Ok = partial(JSONResponse, status_code=200)


@app.route("/")
def home():
    return {"success": True}


@app.route("/reservar", methods=['POST'])
def reservar_handler():
    user = app.current_request.user
    db = app.current_request.db

    reserva = reservar_semana(db, user)
    if reserva.ok:
        return Ok(reserva.data)
    else:
        return Ok(reserva.data)


@app.route("/cancelar_reserva", methods=['POST'])
def reservar_handler():
    user = app.current_request.user
    db = app.current_request.db

    reserva = cancelar_reserva_semana(db, user)
    if reserva.ok:
        return Ok(reserva.data)
    else:
        return Ok(reserva.data)


@app.route("/listar_reservas", methods=['POST'])
def reservar_handler():
    db = app.current_request.db
    reservas = listar_reservas(db)
    return Ok(reservas.data)


@app.route("/mis_reservas", methods=['POST'])
def mis_reservar_handler():
    db = app.current_request.db
    user = app.current_request.user
    reservas = listar_mis_reservas(db, user.username)
    return Ok(reservas.data)