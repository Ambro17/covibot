import hashlib
import hmac
import os
import time

from chalice.app import Request, Response


def validate_request_comes_from_slack(event: Request, get_response):
    # From the list above, because this is an ``http`` event
    # type, we know that event will be of type ``chalice.Request``.

    if os.getenv('TESTING'):
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


def add_user_to_context(event, get_response):
    # Add user to context somehow
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

