import os
from dataclasses import dataclass
from typing import Optional


@dataclass(frozen=True)
class Config:
    sqs_url: str
    sqs_queue_name: str
    slack_bot_token: str
    slack_signing_secret: str
    testing: bool
    production: bool
    log_level: str
    db_url: Optional[str] = None


config = Config(
    sqs_url=os.environ['SQS_URL'],
    sqs_queue_name=os.environ['SQS_QUEUE_NAME'],
    slack_bot_token=os.environ['SLACK_BOT_TOKEN'],
    slack_signing_secret=os.environ['SLACK_SIGNING_SECRET'],
    testing=os.getenv('TESTING', False),
    production=os.getenv('PRODUCTION', False),
    log_level=os.getenv('LOG_LEVEL', 'DEBUG'),
    db_url=os.getenv('DB_URL', None),
)
