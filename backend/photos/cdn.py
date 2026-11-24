"""Photos and videos through CloudFront.

S3 keys are media/c<couple>/<jar>/<memory>/<random>.<ext>, and CloudFront serves the bucket (kept private,
read only by CloudFront) at the same path: https://<site>/media/c<couple>/…. A browser may read a file only
with CloudFront signed cookies whose policy allows media/c<its couple>/*; POST /api/photos/access/ sets them
(valid MEDIA_COOKIE_MAX_AGE, refreshed whenever the app loads), logout clears them. The browser sends them by
itself, so <img> and <video> (with seeking) load straight from the nearest edge, cached there.

Without MEDIA_CDN_* settings (local dev, or before CloudFront is set up) files go through the API instead.
"""
import base64
import json
import time
from functools import lru_cache
from django.conf import settings

PREFIX = 'media/'
COOKIE_PATH = '/media/'
COOKIES = ('CloudFront-Policy', 'CloudFront-Signature', 'CloudFront-Key-Pair-Id')

def enabled():
    return bool(settings.MEDIA_CDN_KEY_ID and settings.MEDIA_CDN_PRIVATE_KEY)

def url(key):
    """The CDN URL of an object, or None when it isn't served by the CDN (CDN off, or a key from before
    the media/c<couple>/ layout that hasn't been moved yet: it keeps going through the API)."""
    return f'/{key}' if enabled() and key.startswith(PREFIX) else None

def _b64(data):
    # CloudFront's URL-safe base64: + = / become - _ ~
    return base64.b64encode(data).decode().translate(str.maketrans('+=/', '-_~'))

@lru_cache(maxsize=1)
def _private_key(encoded):
    from cryptography.hazmat.primitives import serialization
    return serialization.load_pem_private_key(base64.b64decode(encoded), password=None)

def cookies(couple_id, now=None):
    """{name: value} of the signed cookies allowing media/c<couple_id>/* until now + MEDIA_COOKIE_MAX_AGE."""
    from cryptography.hazmat.primitives import hashes
    from cryptography.hazmat.primitives.asymmetric import padding
    expires = int(now if now is not None else time.time()) + settings.MEDIA_COOKIE_MAX_AGE
    statement = {'Resource': f'https://*/{PREFIX}c{couple_id}/*', 'Condition': {'DateLessThan': {'AWS:EpochTime': expires}}}
    policy = json.dumps({'Statement': [statement]}, separators=(',', ':')).encode()
    signature = _private_key(settings.MEDIA_CDN_PRIVATE_KEY).sign(policy, padding.PKCS1v15(), hashes.SHA1())  # what CloudFront verifies
    return {'CloudFront-Policy': _b64(policy), 'CloudFront-Signature': _b64(signature), 'CloudFront-Key-Pair-Id': settings.MEDIA_CDN_KEY_ID}

def set_cookies(response, couple_id):
    for name, value in cookies(couple_id).items():
        response.set_cookie(name, value, max_age=settings.MEDIA_COOKIE_MAX_AGE, path=COOKIE_PATH, secure=True, httponly=True, samesite='Lax')

def clear_cookies(response):
    for name in COOKIES:
        response.delete_cookie(name, path=COOKIE_PATH, samesite='Lax')
