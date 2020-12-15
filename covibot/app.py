import hashlib
import hmac
import os
import time
from dataclasses import dataclass

from chalicelib.bus import SQSBus
from chalicelib.db import get_database, User
from chalicelib.events import StartVMs

from chalice import Chalice, Response
from chalice.app import Request
from slack_sdk import WebClient as Slack

# There's only one lambda created for all @app.route's
# See: https://aws.github.io/chalice/topics/configfile.html#lambda-specific-configuration
app = Chalice(app_name="covibot-api")


@dataclass(frozen=True)
class Config:
    sqs_url: str
    sqs_queue_name: str
    slack_bot_token: str
    slack_signing_secret: str
    testing: bool


config = Config(
    sqs_url=os.environ['SQS_URL'],
    sqs_queue_name=os.environ['SQS_QUEUE_NAME'],
    slack_bot_token=os.environ['SQS_URL'],
    slack_signing_secret=os.environ['SQS_URL'],
    testing=os.getenv('TESTING', False),
)

bus = SQSBus(config.sqs_url, config.sqs_queue_name)
slack = Slack(token=config.slack_bot_token)


@app.middleware('http')
def validate_request_comes_from_slack(event: Request, get_response):
    # From the list above, because this is an ``http`` event
    # type, we know that event will be of type ``chalice.Request``.

    if config.testing:
        # Do not validate on testing environment
        return get_response(event)

    # Read request headers and reject it if it's too old
    headers = event.headers
    print('Headers:\n %r', headers)

    try:
        request_hash = headers['X-Slack-Signature']
        timestamp = headers['X-Slack-Request-Timestamp']
    except KeyError:
        return Response('Missing required headers', status_code=401)

    if abs(time.time() - int(timestamp)) > 60 * 2:
        return Response('Request too old', status_code=400)

    if not verify_signature(event.raw_body, timestamp, request_hash, os.environ['SIGNING_SECRET']):
        print("Request authenticity failed")
        return Response('You are not authorized.', status_code=401)

    print("Request is valid")
    return get_response(event)


@app.middleware('all')
def log_all_traffic(event, get_response):
    start = time.time()

    print('Started processing event')
    response = get_response(event)
    print('Finished processing event.')

    total = time.time() - start
    print(f'Total Seconds: {total:2.f}')
    return response


def verify_signature(request_body, timestamp, signature, signing_secret):
    """Verify the request signature of the request sent from Slack"""
    # Generate a new hash using the app's signing secret, the request timestamp and data
    req = f'v0:{timestamp}:'.encode('utf-8') + request_body
    request_hash = 'v0=' + hmac.new(
        signing_secret.encode('utf-8'),
        req,
        hashlib.sha256
    ).hexdigest()

    return hmac.compare_digest(request_hash, signature)


@app.route("/")
def home():
    return {"success": True}


@app.route("/slack")
def slack_echo():
    try:
        response = slack.chat_postMessage(channel='#random', text="Hello world!")
        print(response)
        message = '✔️ Success!'
    except Exception as e:
        print(repr(e))
        message = '❌ Error'

    return Response(message, status_code=200)


@app.route("/task", name='some_task', methods=['POST'])
def task():
    # Launch sqs task
    args = app.current_request.json_body
    print(f"Received POST with args: {args}")
    if not args:
        return {'success': False, 'error': 'POST must have application/json as content type'}

    event = StartVMs(
        vms=args.get('vms', {}),
        user_id=args.get('user_ids', [-1])
    )

    try:
        bus.send(event)
    except Exception as e:
        print(repr(e))
        return {'exception': repr(e), 'success': False}

    return {"success": True}


@app.route("/db")
def test_db():
    db = get_database()
    user: User = db.get_user(17)
    return {
        'success': True,
        'user': user.username if user else 'Not Found'
    }


@app.on_sqs_message(queue=bus.queue_name, name='start_callback')
def execute_task(event):
    print("Event %r", event.to_dict())
    for record in event:
        print("Message body: %s" % record.body)
