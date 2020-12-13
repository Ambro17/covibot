from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import List, Optional

import boto3
import botocore

dynamodb = boto3.resource('dynamodb')


def create_table(tablename):
    def string_type(name):
        return {
            'AttributeName': name,
            'AttributeType': 'S'
        }

    def key(name):
        return {
            'AttributeName': name,
            'KeyType': 'HASH'
        }

    try:
        table = dynamodb.create_table(
            TableName=tablename,
            KeySchema=[
                key('user_id'),

            ],
            AttributeDefinitions=[
                string_type('user_id'),
            ],
            ProvisionedThroughput={
                'ReadCapacityUnits': 5,
                'WriteCapacityUnits': 5
            }
        )
    except botocore.exceptions.ClientError as error:
        if error.response['Error']['Code'] == 'ResourceInUseException':
            print(f'Table {tablename} Already exists!')
            return dynamodb.Table(tablename)
        else:
            raise

    # Wait until the table exists.
    table.meta.client.get_waiter('table_exists').wait(TableName=tablename)
    print(table.item_count)
    return table


@dataclass
class User:
    id: str
    username: str


@dataclass
class Reserva:
    name: str
    dia: str


class Repository(ABC):

    @abstractmethod
    def get_user(self, user_id) -> Optional[User]:
        ...

    def reservar(self) -> bool:
        ...

    def list_reservas(self) -> List[Reserva]:
        ...


class DynamoDBPersistence(Repository):

    def __init__(self, client):
        self.dynamodb = client

    def get_user(self, user_id) -> Optional[User]:
        data = self.dynamodb.Table('users').get_item(Key={'user_id': str(user_id)})
        user = data.get('Item')
        if not user:
            return

        return User(user['user_id'], user.get('name', 'Unknown'))


def get_database():
    return DynamoDBPersistence(client=boto3.resource('dynamodb'))
