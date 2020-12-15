from abc import ABC, abstractmethod
from .events import Event
import boto3


class MessageBus(ABC):

    @abstractmethod
    def send(self, event: Event):
        ...


class SQSBus(MessageBus):
    """Send messages to aws SQS for async treatment"""
    def __init__(self, queue: str, name: str):
        self.client = boto3.client('sqs')
        self.queue = queue
        self.queue_name = name

    def send(self, event: Event):
        print(f'Sending message {event.to_json()} to {self.queue}')
        self.client.send_message(
            QueueUrl=self.queue,
            MessageBody=event.to_json()
        )


class TestingBus(MessageBus):
    """Bus to ease testing"""
    def __init__(self, queue: str):
        self.queue = queue
        self.sent = []

    def send(self, event: Event):
        self.sent.append(event)
