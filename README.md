# Covibot (Yes, i was inspired that day)

## Prerequisites
`awscli` installed.

`python3.6+`

For development:
- Docker
- Docker-Compose
- `jq` Command Utility
- `direnv` to load env vars based on current dir


## Work Items
- [x] Add Dynamodb persistence
- [x] Connect to slack. Adapt response to slack.
- [x] HTTP Middleware that logs and validates slack request signature
- [x] Implement `/reservar` & `/cancelar` Phase 1
- [x] Implement `/mis_reservas` and `/list_reservas`
- [x] Implement max amount of reservas per day.
- [x] Implement docker-compose with local dynamodb
- [x] Implement Slack to Container communication for faster development (powered by ngrok)
- [x] Implement user crud in a happy way to be flexible to policy changes (populate py script)
- [ ] Deploy to slack
- [ ] Implement `/reservar` Phase 2 with availability per sections

Low priority

- [x] Reduce lambda role rights to minumum working version (Already minimum)
- [x] Add tests
- []  Add db-shell target to crud users and reservas

## Install
```
python3.7 -m venv env && source env/bin/activate
pip install -r requirements.txt
```
Create temporary aws access key with google single sign on
```
aws-google-auth -u $USER@onapsis.com -I C019my1yt -S 837142051107 --ask-role --duration 3600 --save-failure-html
```
It will ask you to confirm on a device you have the linked account.
Then choose the role that has access to the services. If you don't know which one, ask @nambrosini
> Credentials will be saved on `~/.aws/credentials` with the profile `sts`.
> You may want to change the profile name to `default` to avoid passing the profile on each command

> Note: The access key is valid for just 1 hour. After that you must recreate it with the same command

You can check the credentials work correctly with
```bash
aws sts get-caller-identity
```
It should return something like
```json
{
    "UserId": "ABCDEFG:user@onapsis.com",
    "Account": "123456789",
    "Arn": "arn:aws:sts::123456:assumed-role/ROLE_NAME/user@onapsis.com"
}
```


## Usage
Add your new handler on `covibot/app.py` and then run
```
chalice deploy
```
To remove the deployed resources 
```
chalice delete
```
Package into terraform template
```
cd covibot
chalice package --pkg-format terraform .build
```

## Create SQS queue
`aws sqs create-queue --queue-name queue-name`
or follow the docs:
https://docs.aws.amazon.com/AWSSimpleQueueService/latest/SQSDeveloperGuide/sqs-configure-create-queue.html

Then save the sqs url and queue name under env vars with your method of choice
```bash
export SQS_URL=full_url
export SQS_QUEUE_NAME=lacola
```

It is recommended to install `direnv` and create and `.envrc` file in order to automatically load
environment variables when you enter the project. This effectively drops the necessity of python-dotenv


## View logs

Api Handler logs

```
chalice logs
```

Tasks logs

```
chalice logs -n start_callback # or the task name function
```

## Local Development

Install `direnv` and create an .envrc on project root with the following content

```
dotenv
```

This loads secrets from an `.env` file on the same dir. Go ahead and create it with the real secrets:

```
SLACK_BOT_TOKEN=xoxb-...
SLACK_SIGNING_SECRET=73...
SQS_URL=https://sqs.
SQS_QUEUE_NAME=testkiu
PYTHONPATH=covibot
TESTING=1
DB_URL=localhost:8000
```

Then run

```
docker-compose up
```

And search the logs for ngrok's public url to start playing with it. Covibot source folder is mounted on the app
container so changes should be reflected without needing to restart the containers.

## Troubleshooting

If ngrok fails to start when you run `docker-compose up`, it may be a docker dns problem. To solve it edit
your `/etc/docker/daemon.json` and put google dns as the first server.

```
{"dns": ["8.8.8.8", ...]}  # Any other dns server you may have must go after google's
```

## Testing

You can use docker-compose to run tests in an isolated manner, with automatic service management _or_ manually starting
dynamodb container and then running tests. I recommend the first one:
```docker-compose run --rm covibot pytest```
For the second one:

```
docker-compose up dynamodb
pytest
```
