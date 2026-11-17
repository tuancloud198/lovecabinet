import logging
import uuid
from django.conf import settings
from django.contrib.auth import authenticate
from django.db import transaction
from rest_framework.authtoken.models import Token
from rest_framework.exceptions import APIException, ValidationError
from users.models import User

def create_user(data):
    return User.objects.create_user(**data)
@transaction.atomic
def register_user(serializer):
    user = serializer.save()
    return user, Token.objects.create(user=user).key

def login_user(username, password):
    user = authenticate(username=username, password=password)
    if not user:
        raise ValidationError('Tên đăng nhập hoặc mật khẩu không đúng.')
    return user, Token.objects.get_or_create(user=user)[0].key

logger = logging.getLogger(__name__)
# Tolerate small clock differences between this server and Google (the library default is 0s,
# so a server a few seconds behind rejects fresh tokens as "used too early").
GOOGLE_CLOCK_SKEW_SECONDS = 60

class GoogleUnavailable(APIException):
    status_code = 503
    default_detail = 'Không kết nối được tới Google, vui lòng thử lại sau.'

def _google_request(timeout=10):
    from google.auth.transport import requests as google_requests
    class Request(google_requests.Request):
        def __call__(self, *args, **kwargs):
            kwargs.setdefault('timeout', timeout)  # the library default is 120s, longer than gunicorn's worker timeout
            return super().__call__(*args, **kwargs)
    return Request()

def verify_google_credential(credential):
    """Check a Google Identity Services ID token and return its claims."""
    if not settings.GOOGLE_CLIENT_ID:
        raise ValidationError('Đăng nhập Google chưa được bật.')
    from google.auth.exceptions import TransportError
    from google.oauth2 import id_token
    try:
        claims = id_token.verify_oauth2_token(credential, _google_request(), settings.GOOGLE_CLIENT_ID, clock_skew_in_seconds=GOOGLE_CLOCK_SKEW_SECONDS)
    except TransportError:
        # Google's signing keys couldn't be fetched (no internet / proxy not set): fail fast, don't hang.
        raise GoogleUnavailable()
    except ValueError as exc:
        logger.warning('Google ID token rejected: %s', exc)
        raise ValidationError('Không xác thực được tài khoản Google.')
    if not claims.get('email_verified'):
        raise ValidationError('Email Google chưa được xác minh.')
    return claims

@transaction.atomic
def google_login(credential):
    """Sign in (or sign up) with a Google ID token. Returns (user, token, created)."""
    claims = verify_google_credential(credential)
    user = User.objects.filter(google_sub=claims['sub']).first()
    created = user is None
    if created:
        email = claims['email'].lower()
        username = email if not User.objects.filter(username=email).exists() else f'{email[:100]}-{uuid.uuid4().hex[:8]}'
        user = User(username=username[:150], email=email, google_sub=claims['sub'], display_name=(claims.get('name') or email.split('@')[0])[:100])
        user.set_unusable_password()
        user.save()
    if not user.is_active:
        raise ValidationError('Tài khoản đã bị khóa.')
    return user, Token.objects.get_or_create(user=user)[0].key, created

def update_profile(serializer):
    return serializer.save()

def logout_user(token):
    token.delete()
