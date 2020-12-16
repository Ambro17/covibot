from functools import partial

from chalice import Chalice, Response
from slack_sdk import WebClient as Slack

from chalicelib.bus import SQSBus
from chalicelib.config import config
from chalicelib.middlewares import (
    validate_request_comes_from_slack,
    log_all_traffic,
    add_user_to_context,
)
from chalicelib.db import get_database
from chalicelib.reservas.api import reservar_dia, DIA


def init_app():
    app = Chalice(app_name="covibot-api")

    # Middlewares
    app.register_middleware(validate_request_comes_from_slack, 'http')
    app.register_middleware(add_user_to_context, 'http')
    app.register_middleware(log_all_traffic, 'all')

    app.db  = get_database()
    app.bus = SQSBus(queue=config.sqs_url, name=config.sqs_queue_name)
    app.slack = Slack(token=config.slack_bot_token)

    return app


app = init_app()

JSONResponse = partial(Response, headers={'Content-Type': 'application/json'})
Ok = partial(JSONResponse, status_code=200)


@app.route("/")
def home():
    return {"success": True}


@app.route("/reservar")
def reservar_handler():
    args = app.current_request.json_body
    if not args:
        return JSONResponse('Missing application/json Content-Type', status_code=400)

    db = get_database()

    user_id = '1'
    user = db.get_user(user_id)
    if not user:
        # Slack only return responses with status 200.
        # So all messages directed to users should use it.
        return Ok('Unable to find user')

    dia_reserva: DIA = 'L'
    reserva = reservar_dia(db, user_id, dia_reserva)
    if reserva.otorgada:
        return Ok(f'✔️ Reserva realizada para `{dia_reserva}`!')
    else:
        print(reserva.mensaje)
        return Ok('❌ La reserva no pudo ser realizada.')
