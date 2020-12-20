"""
Populate local dynamodb database
Assumes tables were already created calling bash create_tables.sh
"""
import os
import sys
from pprint import pprint

import boto3

print("Connecting to database @ %s" % os.getenv('DB_URL'))
dynamo = boto3.resource('dynamodb', endpoint_url=os.getenv('DB_URL'))


def edit_user(user_id, group, name, **kwargs):
    resp = dynamo.Table('users').put_item(
        Item={'user_id': user_id, 'group': group, 'name': name, **kwargs}
    )
    assert resp['ResponseMetadata']['HTTPStatusCode'] == 200, "Error creating user. %r" % resp
    return resp.get('Item', 'Item Not found!')


def create_users():
    users = [
        {'user_id': '1', 'group': 1, 'name': 'Shakira'},
        {'user_id': '2', 'group': 1, 'name': 'Lerner'},
        {'user_id': '3', 'group': 2, 'name': 'Piazzola'},
        {'user_id': '4', 'group': 2, 'name': 'G Sony'},
    ]
    for user in users:
        resp = dynamo.Table('users').put_item(
            Item=user
        )
        assert resp['ResponseMetadata']['HTTPStatusCode'] == 200, "Error creating user. %r" % resp

    print("All users created")
    return dynamo.Table('users').scan()


if __name__ == '__main__':
    args = sys.argv[1:]
    if not args:
        create_users()
    else:
        pprint(dynamo.Table('users').scan()['Items'])
