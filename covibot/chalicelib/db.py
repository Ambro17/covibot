from abc import ABC, abstractmethod
from dataclasses import dataclass
from datetime import datetime
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
    group: int
    username: str


@dataclass
class Reserva:
    name: str
    dia: str


@dataclass
class SolicitudReserva:
    otorgada: bool
    mensaje: str


@dataclass
class SolicitudCancelacion:
    cancelada: bool
    mensaje: str


class Repository(ABC):

    @abstractmethod
    def get_user(self, user_id) -> Optional[User]:
        ...

    @abstractmethod
    def reservar_dia(self, username: str, date: str) -> SolicitudReserva:
        ...

    @abstractmethod
    def reservar_dias(self, username: str, dates: List[str]) -> SolicitudReserva:
        ...

    @abstractmethod
    def cancelar_reserva_dias(self, username, dates: List[str]) -> SolicitudCancelacion:
        ...

    @abstractmethod
    def list_reservas(self) -> List[Reserva]:
        ...

    @abstractmethod
    def mis_reservas(self, username: str) -> List[Reserva]:
        ...


class DynamoDBPersistence(Repository):

    def __init__(self, client):
        self.dynamodb = client
        self.users = client.Table('users')
        self.reservas = client.Table('reservas')

    def get_user(self, user_id) -> Optional[User]:
        data = self.users.get_item(Key={'user_id': str(user_id)})
        user = data.get('Item')
        if not user:
            return

        return User(user['user_id'], user.get('group', 1), user.get('name', 'Unknown'))


    def reservar_dia(self, username: str, date: str) -> SolicitudReserva:
        if not date:
            return SolicitudReserva(otorgada=False, mensaje='No se especificó el día a reservar')

        print(f'{username!r} - {date!r}')
        resp = self.reservas.update_item(
            Key={'date': date},
            UpdateExpression="ADD reservas :r",
            ExpressionAttributeValues={
                ':r': {username},
            },
            ReturnValues='ALL_NEW',
        )
        if not resp.get('Attributes', {}).get('reservas'):
            print(f'[ERROR] {resp!r}')
            return SolicitudReserva(otorgada=False, mensaje='Error realizando la reserva.')

        return SolicitudReserva(True, f'Se reservó el día `{date}` para {username}')


    def reservar_dias(self, username: str, dates: List[str]) -> SolicitudReserva:
        """Dado un usuario y su grupo, asignarle reserva para esa semana"""
        if not dates:
            return SolicitudReserva(otorgada=False, mensaje='No se especificaron los días a reservar')

        for date in dates:
            resp = self.reservar_dia(username, date)

        if not resp.otorgada:
            return SolicitudReserva(otorgada=False, mensaje='Error realizando la reserva.')

        return SolicitudReserva(True, f'Se reservaron los dias `{dates}` para {username}')


    def cancelar_reserva_dias(self, username, dates: List[str]) -> SolicitudCancelacion:
        for date in dates:
            resp = self.reservas.update_item(
                Key={'date': date},
                UpdateExpression="DELETE reservas :r",
                ExpressionAttributeValues={
                    ':r': {username},
                },
                ReturnValues='ALL_NEW',
            )
            if not resp.get('Attributes'):
                # Reservas are allowed to be empty after cancellation
                # But Attributes must be returned if the operation was successfull
                print(f'[ERROR] {resp!r}')
                return SolicitudCancelacion(cancelada=False, mensaje='Error cancelando la reserva.')

        return SolicitudCancelacion(cancelada=True, mensaje='La reserva fue cancelada.')


    def list_reservas(self) -> List[Reserva]:
        items = self.reservas.scan()['Items']
        return [
            Reserva(name=username, dia=item['date'])
            for item in items
            for username in item.get('reservas', [])
        ]


    def mis_reservas(self, username: str) -> List[Reserva]:
        all_reservas = self.list_reservas()
        return [
            reserva for reserva in all_reservas
            if reserva.name == username and
               datetime.strptime(reserva.dia, '%Y-%m-%d').date() >= datetime.now().date()
        ]


class MemoryPersistence(Repository):
    """Interface used for testing"""

    def __init__(self, users: dict = None, reservas: list = None):
        self.users = users
        self.reservas: List[Reserva] = reservas or []

    def get_user(self, user_id) -> Optional[User]:
        user = self.users.get(user_id)
        if user:
            return User(**self.users.get(user_id))
        else:
            return None

    def reservar_dia(self, username: str, date: str) -> SolicitudReserva:
        self.reservas.append(Reserva(username, date))
        return SolicitudReserva(True, 'Testing OK')

    def reservar_dias(self, username: str, dates: List[str]) -> SolicitudReserva:
        for dia in dates:
            reserva = Reserva(name=username, dia=dia)
            if reserva not in self.reservas:
                self.reservas.append(reserva)

        return SolicitudReserva(True, 'Testing OK')


    def cancelar_reserva_dias(self, username, dates: List[str]) -> SolicitudCancelacion:
        self.reservas = [r for r in self.reservas if r.dia not in dates]
        return SolicitudCancelacion(True, 'MOCKED')


    def list_reservas(self) -> List[Reserva]:
        return self.reservas

    def mis_reservas(self, username: str) -> List[Reserva]:
        return [x for x in self.reservas if x.name == username]

def get_database():
    return DynamoDBPersistence(client=boto3.resource('dynamodb'))
