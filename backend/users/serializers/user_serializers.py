from django.contrib.auth.password_validation import validate_password
from django.core.exceptions import ValidationError as DjangoValidationError
from rest_framework import serializers
from users.models import User
class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'username', 'tag', 'display_name', 'birth_date', 'bio', 'gender']
        read_only_fields = ['id', 'username', 'tag']
class RegisterSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True)
    class Meta:
        model = User
        fields = ['username', 'password', 'display_name', 'birth_date', 'bio', 'gender']
    def validate_password(self, value):
        try:
            validate_password(value)
        except DjangoValidationError as exc:
            raise serializers.ValidationError(exc.messages)
        return value
    def create(self, data):
        from users.services import create_user
        return create_user(data)

class GoogleLoginSerializer(serializers.Serializer):
    credential = serializers.CharField(max_length=4096)

class LoginSerializer(serializers.Serializer):
    username = serializers.CharField(max_length=150)
    password = serializers.CharField(write_only=True)
