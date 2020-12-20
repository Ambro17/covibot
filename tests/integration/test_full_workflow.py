"""
This tests aim to be representative of the production environment.
Mocks, Fakes, etc should be avoided to keep environment
as close to production as possible
"""
from functools import partial
from textwrap import dedent

import pytest
from chalice.test import Client
from freezegun import freeze_time

from chalicelib.db import get_client
from covibot.app import app


@pytest.fixture(scope='function')
def client():
    with Client(app) as client:
        client.post_form = partial(client.http.post,
                                   headers={'content-type': 'application/x-www-form-urlencoded'}
                                   )
        yield client
        dynamodb = get_client()
        delete_from_table(dynamodb.Table('reservas'))


def delete_from_table(table):
    resp = table.scan()
    with table.batch_writer() as batch:
        for item in resp['Items']:
            batch.delete_item(Key={'date': item['date']})

    assert table.scan()['Items'] == [], f"There are still elements on {table}"


def select_all_from_table(table):
    return table.scan()['Items']


def create_user(dynamo_resource, user_id, group, name, **kwargs):
    resp = dynamo_resource.Table('users').put_item(
        Item={'user_id': user_id, 'group': group, 'name': name, **kwargs}
    )
    assert resp['ResponseMetadata']['HTTPStatusCode'] == 200, "Error creating user. %r" % resp
    return resp.get('Item', 'Item Not found!')


def delete_user(dynamo_resource, user_id):
    resp = dynamo_resource.Table('users').delete_item(Key={'user_id': user_id})
    assert resp['ResponseMetadata']['HTTPStatusCode'] == 200, "Error deleting user"


def test_reservar(client):
    params = 'user_id=1&another_param=2'
    resp = client.post_form('/reservar', body=params)
    assert b'Reserva Realizada' in resp.body


def test_cancelar_reserva(client):
    params = 'user_id=2'
    resp = client.post_form('/cancelar_reserva', body=params)
    assert b'Reserva Cancelada' in resp.body


def test_ver_mis_reservas_empty(client):
    params = 'user_id=3&other_param=1&c=3'
    resp = client.post_form('/mis_reservas', body=params)
    assert 'No tenés ninguna reserva aún' in resp.body.decode('utf-8')


@freeze_time("2020-12-20")
def test_ver_mis_reservas_non_empty(client):
    # Create reserva for user 1
    params = 'user_id=1'
    resp = client.post_form('/reservar', body=params)
    assert b'Reserva Realizada' in resp.body

    reservas = client.post_form('/mis_reservas', body=params)
    assert reservas.body.decode('utf-8') == dedent("""```
2020-12-23
    Juan
2020-12-22
    Juan
2020-12-21
    Juan
```""")


def test_ver_todas_las_reservas(client):
    params = 'user_id=4'
    resp = client.post_form('/listar_reservas', body=params)
    assert 'No tenés ninguna reserva aún' in resp.body.decode('utf-8')


@freeze_time("2020-12-20")
def test_ver_todas_las_reservas_from_two_users(client):
    params = 'user_id=1'
    resp = client.post_form('/reservar', body=params)
    assert b'Reserva Realizada' in resp.body

    params = 'user_id=2'
    resp = client.post_form('/reservar', body=params)
    assert b'Reserva Realizada' in resp.body

    resp = client.post_form('/listar_reservas', body=params)
    expected = """```
2020-12-24
    Second
2020-12-23
    Juan
2020-12-22
    Juan
2020-12-21
    Juan
2020-12-25
    Second
```"""
    assert resp.body.decode('utf-8') == expected


@freeze_time("2020-12-20")
def test_reservar_ver_cancelar_ver_listar_reservas(client):
    # En principio no tengo reservas
    params = 'user_id=1'
    resp = client.post_form('/mis_reservas', body=params)
    assert 'No tenés ninguna reserva aún' in resp.body.decode('utf-8')

    # Reservo
    params = 'user_id=1'
    resp = client.post_form('/reservar', body=params)
    assert b'Reserva Realizada' in resp.body

    # Mis reservas
    resp = client.post_form('/mis_reservas', body=params)
    assert resp.body.decode('utf-8') == '```\n2020-12-23\n    Juan\n2020-12-22\n    Juan\n2020-12-21\n    Juan\n```'

    # Cancelar
    resp = client.post_form('/cancelar_reserva', body=params)
    assert b'Reserva Cancelada' in resp.body

    # Listar Todas
    resp = client.post_form('/listar_reservas', body=params)
    assert 'No tenés ninguna reserva aún' in resp.body.decode('utf-8')

    # Y las mias también por las dudas..
    resp = client.post_form('/mis_reservas', body=params)
    assert 'No tenés ninguna reserva aún' in resp.body.decode('utf-8')
