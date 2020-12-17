import logging
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
from chalicelib.reservas.api import reservar_semana, cancelar_reserva_semana


def init_app(config: Config):
    app = Chalice(app_name="covibot-api")
    app.log.setLevel(config.log_level)

    # Middlewares
    app.register_middleware(validate_request_comes_from_slack, 'http')
    app.register_middleware(add_user_to_context, 'http')
    app.register_middleware(log_all_traffic, 'all')

    app.db  = get_database()
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

    reserva = reservar_semana(db, user.id)
    if reserva.ok:
        return Ok(f'✔️ Reserva realizada para `{reserva.days}`!')
    else:
        return Ok(f'❌ La reserva no pudo ser realizada. Error: {reserva.message}')


@app.route("/cancelar_reserva", methods=['POST'])
def reservar_handler():
    user = app.current_request.user
    db = app.current_request.db

    reserva = cancelar_reserva_semana(db, user.id)
    if reserva.ok:
        return Ok(f'✔️ Reserva realizada para `{reserva.data}`!')
    else:
        return Ok(f'❌ La reserva no pudo ser realizada. Error: {reserva.data}')


