import os

from chalicelib.bus import SQSBus
from chalicelib.db import get_database, User
from chalicelib.events import StartVMs

from chalice import Chalice, Response
from slack_sdk import WebClient as Slack


# There's only one lambda created for all @app.route's
# See: https://aws.github.io/chalice/topics/configfile.html#lambda-specific-configuration
app = Chalice(app_name="covibot-api")
bus = SQSBus(os.environ['SQS_URL'], os.environ['SQS_QUEUE_NAME'])
slack = Slack(token=os.environ['SLACK_BOT_TOKEN'])


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
