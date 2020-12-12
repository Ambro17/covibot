# Covibot (Yes, really creative)

## Prerequisites
`awscli` installed.
`python3.6+`

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
chalice package --pkg-format terraform terraform_artifact
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
