from django.http import FileResponse
from rest_framework import viewsets
from rest_framework.decorators import action
from rest_framework.response import Response
from common.services import couple_for
from photos.models import Photo
from photos.serializers.photo_serializers import PhotoSerializer, UploadSerializer
from photos.services import upload_photo, read_photo, delete_photo
class PhotoViewSet(viewsets.GenericViewSet):
    serializer_class = PhotoSerializer
    def get_queryset(self):
        return Photo.objects.filter(memory__jar__cabinet__couple=couple_for(self.request.user))
    def create(self, request):
        serializer = UploadSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        photo = upload_photo(request.user, serializer.validated_data['memory'], serializer.validated_data['file'])
        return Response(PhotoSerializer(photo).data, status=201)
    @action(detail=True, methods=['get'])
    def content(self, request, pk=None):
        photo = self.get_object()
        response = FileResponse(read_photo(photo), content_type=photo.content_type)
        response['Cache-Control'] = 'private, max-age=300'
        response['X-Content-Type-Options'] = 'nosniff'
        return response
    def destroy(self, request, pk=None):
        delete_photo(self.get_object())
        return Response(status=204)
