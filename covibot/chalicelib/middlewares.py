import hashlib
import hmac
import os
import time
from functools import partial
from urllib.parse import parse_qsl

from chalice.app import Request, Response

from chalicelib.config import config
from chalicelib.db import get_database

JSONResponse = partial(Response, headers={'Content-Type': 'application/json'})
Ok = partial(JSONResponse, status_code=200)


def validate_request_comes_from_slack(event: Request, get_response):
    """To be used only as http middleware, as it expects a Request event"""

    if config.testing:
        # Do not validate on testing environment
        return get_response(event)

    # Read request headers and reject it if it's too old
    headers = event.headers
    print('Headers:\n %r', headers)

    try:
        request_hash = headers['X-Slack-Signature']
        timestamp = headers['X-Slack-Request-Timestamp']
    except KeyError:
        return Response('Missing required headers', status_code=401)

    if abs(time.time() - int(timestamp)) > 60 * 2:
        return Response('Request too old', status_code=400)

    if not verify_signature(event.raw_body, timestamp, request_hash, os.environ['SIGNING_SECRET']):
        print("Request authenticity failed")
        return Response('You are not authorized.', status_code=401)

    print("Request is valid")
    return get_response(event)


def log_all_traffic(event, get_response):
    start = time.time()

    print('Started processing event')
    response = get_response(event)
    print('Finished processing event.')

    total = time.time() - start
    print(f'Total Seconds: {total:.1f}')
    return response


def add_user_to_context(event: Request, get_response):
    # Add user to context somehow
    if event.method != 'POST':
        return get_response(event)
    if 'application/x-www-form-urlencoded' not in event.headers.get('Content-Type', ''):
        return JSONResponse("Only form encoded payloads are allowed.", status_code=400)

    try:
        args = dict(parse_qsl(event.raw_body.decode()))
    except Exception:
        return JSONResponse('Invalid Form Data', status_code=400)

    if not args or not args.get('user_id'):
        return JSONResponse('Missing "user_id" FORM key', status_code=400)

    user_id = args['user_id']
    db = get_database()
    user = db.get_user(user_id)
    if not user:
        # Slack only return responses with status 200.
        # So all messages directed to users should status 200.
        return Ok(f'Unable to find user with id `{user_id!r}`')

    if not user.group:
        return Ok(f'User `{user_id!r}` has no current group assigned')

    if user.group not in {1, 2}:
        return Ok(f'Invalid group `{user.group!r}` for {user.id}')

    # Attach user to request offset for easier access
    event.user = user

    return get_response(event)


def verify_signature(request_body, timestamp, signature, signing_secret):
    """Verify the request signature of the request sent from Slack"""
    # Generate a new hash using the app's signing secret, the request timestamp and data
    req = f'v0:{timestamp}:'.encode('utf-8') + request_body
    request_hash = 'v0=' + hmac.new(
        signing_secret.encode('utf-8'),
        req,
        hashlib.sha256
    ).hexdigest()

    return hmac.compare_digest(request_hash, signature)

