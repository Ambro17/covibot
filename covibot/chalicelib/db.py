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
    group: str
    username: str


@dataclass
class Reserva:
    name: str
    dia: str

@dataclass
class SolicitudReserva:
    otorgada: bool
    mensaje: str


class Repository(ABC):

    @abstractmethod
    def get_user(self, user_id) -> Optional[User]:
        ...

    @abstractmethod
    def reservar_dia(self, user_id: str, date: str) -> SolicitudReserva:
        ...

    @abstractmethod
    def reservar_dias(self, user_id: str, dates: List[str]) -> SolicitudReserva:
        ...

    def cancelar_reserva(self) -> bool:
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

        return User(user['user_id'], user.get('username', 'Unknown'))


    def reservar_dia(self, user_id: str, date: str) -> SolicitudReserva:
        return SolicitudReserva(True, 'MOCKED')


    def reservar_dias(self, user_id: str, dates: List[str]) -> SolicitudReserva:
        """Dado un usuario y su grupo, asignarle reserva para esa semana"""
        return SolicitudReserva(True, 'Semana')


class MemoryPersistence(Repository):
    """Interface used for testing"""
    def __init__(self, users: dict = None, reservas: list = None):
        self.users = users
        self.reservas = reservas or []

    def get_user(self, user_id) -> Optional[User]:
        user = self.users.get(user_id)
        if user:
            return User(**self.users.get(user_id))
        else:
            return None

    def reservar_dia(self, user_id: str, date: str) -> SolicitudReserva:
        self.reservas.append((user_id, date))
        return SolicitudReserva(True, 'Testing OK')

    def reservar_dias(self, user_id: str, dates: List[str]) -> SolicitudReserva:
        self.reservas.append(
            (user_id, dates)
        )
        return SolicitudReserva(True, 'Testing OK')


def get_database():
    return DynamoDBPersistence(client=boto3.resource('dynamodb'))
