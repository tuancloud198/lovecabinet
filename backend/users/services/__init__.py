from django.contrib.auth import authenticate
from django.db import transaction
from rest_framework.authtoken.models import Token
from rest_framework.exceptions import ValidationError
from ..models import User

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

def update_profile(serializer):
    return serializer.save()

def logout_user(token):
    token.delete()
