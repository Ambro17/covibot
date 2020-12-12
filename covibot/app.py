import logging
import os

from chalice import Chalice
from chalicelib.bus import SQSBus
from chalicelib.events import StartVMs

# There's only one lambda created for all @app.route's
# See: https://aws.github.io/chalice/topics/configfile.html#lambda-specific-configuration
app = Chalice(app_name="covibot-api")
bus = SQSBus(os.getenv('SQS_URL', 'MissingSQSURLEnvVar'))


@app.route("/", name='home')
def home():
    return {"success": True}


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


@app.on_sqs_message(queue=os.getenv('SQS_QUEUE_NAME'), name='start_callback')
def execute_task(event):
    print("Event %r", event.to_dict())
    for record in event:
        print("Message body: %s" % record.body)
