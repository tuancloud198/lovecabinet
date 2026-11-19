from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from django.conf import settings
from users.serializers.user_serializers import UserSerializer, RegisterSerializer, LoginSerializer, GoogleLoginSerializer
from users.services import register_user, login_user, google_login, update_profile, logout_user
@api_view(['POST'])
@permission_classes([AllowAny])
def register(request):
    serializer = RegisterSerializer(data=request.data)
    serializer.is_valid(raise_exception=True)
    user, token = register_user(serializer)
    return Response({'token': token, 'user': UserSerializer(user).data}, status=201)
@api_view(['POST'])
@permission_classes([AllowAny])
def login(request):
    serializer = LoginSerializer(data=request.data)
    serializer.is_valid(raise_exception=True)
    user, token = login_user(**serializer.validated_data)
    return Response({'token': token, 'user': UserSerializer(user).data})
@api_view(['POST'])
@permission_classes([AllowAny])
def google(request):
    serializer = GoogleLoginSerializer(data=request.data)
    serializer.is_valid(raise_exception=True)
    user, token, created = google_login(serializer.validated_data['credential'])
    return Response({'token': token, 'user': UserSerializer(user).data, 'created': created}, status=201 if created else 200)
@api_view(['GET'])
@permission_classes([AllowAny])
def auth_config(request):
    """Public settings the sign-in screen needs (the Google client ID is public by design)."""
    return Response({'google_client_id': settings.GOOGLE_CLIENT_ID, 'version': settings.APP_VERSION})
@api_view(['GET', 'PATCH'])
def me(request):
    serializer = UserSerializer(request.user, data=request.data, partial=True) if request.method == 'PATCH' else UserSerializer(request.user)
    if request.method == 'PATCH':
        serializer.is_valid(raise_exception=True)
        update_profile(serializer)
    return Response(serializer.data)
@api_view(['POST'])
def logout(request):
    logout_user(request.auth)
    return Response(status=204)
