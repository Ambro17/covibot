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


def init_app(config: Config, db=None):
    app = Chalice(app_name="covibot-api")
    app.log.setLevel(config.log_level)

    # Middlewares
    app.register_middleware(add_user_to_context, 'http')
    if config.production:
        app.register_middleware(validate_request_comes_from_slack, 'http')
        app.register_middleware(log_all_traffic, 'all')

    app.db = db or get_database()
    app.bus = SQSBus(queue=config.sqs_url, name=config.sqs_queue_name)
    app.slack = Slack(token=config.slack_bot_token)

    return app


app = init_app(config)

JSONResponse = partial(Response, headers={'Content-Type': 'application/json'})
Ok = partial(JSONResponse, status_code=200)

# Slack slash commands are form-encoded and use the POST method
# https://api.slack.com/interactivity/slash-commands#app_command_handling
slack_command = partial(
    app.route,
    content_types=['application/x-www-form-urlencoded'],
    methods=['POST'],
)


@app.route("/", methods=['POST', 'GET'])
def home():
    return {"success": True}


@slack_command("/reservar")
def reservar_handler():
    user = app.current_request.user
    reserva = reservar_semana(app.db, user)
    if reserva.ok:
        return Ok(reserva.data)
    else:
        return Ok(reserva.data)


@slack_command("/cancelar_reserva")
def cancelar_reserva_handler():
    user = app.current_request.user

    reserva = cancelar_reserva_semana(app.db, user)
    if reserva.ok:
        return Ok(reserva.data)
    else:
        return Ok(reserva.data)


@slack_command("/listar_reservas")
def listar_reservas_handler():
    reservas = listar_reservas(app.db)
    return Ok(reservas.data)


@slack_command("/mis_reservas")
def mis_reservar_handler():
    user = app.current_request.user
    reservas = listar_mis_reservas(app.db, user.username)
    return Ok(reservas.data)
