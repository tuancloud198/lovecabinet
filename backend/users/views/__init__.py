from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from django.conf import settings
from rest_framework.exceptions import ValidationError
from users.models import User
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
@api_view(['POST', 'DELETE'])
def my_avatar(request):
    """POST a photo (multipart `file`) to use it as your picture; DELETE to go back to the character."""
    from users.avatars import remove_avatar, set_avatar
    if request.method == 'DELETE':
        remove_avatar(request.user)
    else:
        upload = request.FILES.get('file')
        if not upload:
            raise ValidationError('Hãy chọn một ảnh.')
        set_avatar(request.user, upload)
    return Response(UserSerializer(request.user).data)
@api_view(['GET'])
def avatar(request, pk):
    from django.http import FileResponse, Http404
    from users.avatars import can_see, read_avatar
    owner = User.objects.filter(pk=pk).first()
    if not owner or not owner.avatar_key or not can_see(request.user, owner):
        raise Http404
    response = FileResponse(read_avatar(owner), content_type='image/jpeg')
    response['Cache-Control'] = 'private, max-age=604800'  # the URL changes with each new picture
    response['X-Content-Type-Options'] = 'nosniff'
    return response
@api_view(['POST'])
def logout(request):
    from photos import cdn
    logout_user(request.auth)
    response = Response(status=204)
    cdn.clear_cookies(response)  # this browser can't load the couple's photos any more
    return response
