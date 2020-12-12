import os

from chalice import Chalice
from chalicelib.bus import SQSBus
from chalicelib.events import StartVMs

# There's an implicit lambda created with the name
# `api_handler` that receives all api gateway traffic
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
    event = StartVMs(vms=args.get('vms', {}), user_id=args.get('user_ids', [-1]))
    bus.send(event)
    return {"success": True}


@app.on_sqs_message(queue=os.getenv('SQS_QUEUE_NAME'), name='start_callback')
def execute_task(event):
    app.log.debug("Event %r", event.to_dict())
    for record in event:
        app.log.info("Message body: %s", record.body)
