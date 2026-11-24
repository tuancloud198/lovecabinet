import re
from botocore.exceptions import ClientError
from django.http import FileResponse, HttpResponse, HttpResponseForbidden, StreamingHttpResponse
from django.shortcuts import get_object_or_404
from django.views.decorators.http import require_GET
from rest_framework import viewsets
from rest_framework.decorators import action
from rest_framework.response import Response
from common.services import couple_for
from photos.models import Photo
from photos.serializers.photo_serializers import PhotoSerializer, StageSerializer, UploadSerializer
from photos.services import upload_photo, stage_photo, read_photo, read_range, delete_photo, valid_stream_signature
class PhotoViewSet(viewsets.GenericViewSet):
    serializer_class = PhotoSerializer
    def get_queryset(self):
        return Photo.objects.filter(memory__jar__cabinet__couple=couple_for(self.request.user))
    def create(self, request):
        serializer = UploadSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        photo = upload_photo(request.user, serializer.validated_data['memory'], serializer.validated_data['file'], serializer.location())
        return Response(PhotoSerializer(photo).data, status=201)
    @action(detail=False, methods=['post'])
    def stage(self, request):
        """Upload a photo for a memory that isn't created yet; returns a token for `staged_photos`."""
        serializer = StageSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        return Response({'token': stage_photo(request.user, serializer.validated_data['file'], serializer.location())}, status=201)
    @action(detail=False, methods=['post'])
    def access(self, request):
        """(Re)set the CDN cookies that let this browser load its couple's photos/videos (photos/cdn.py).
        The app calls it on every load, so they never expire while it's in use."""
        from couples.models import Membership
        from photos import cdn
        membership = Membership.objects.filter(user=request.user).first()
        response = Response({'cdn': cdn.enabled() and membership is not None})
        if response.data['cdn']:
            cdn.set_cookies(response, membership.couple_id)
        else:
            cdn.clear_cookies(response)
        return response
    @action(detail=True, methods=['get'])
    def content(self, request, pk=None):
        photo = self.get_object()
        body, content_type = read_photo(photo, request.query_params.get('size'))
        response = FileResponse(body, content_type=content_type)
        response['Cache-Control'] = 'private, max-age=31536000, immutable'  # a photo's bytes never change
        response['X-Content-Type-Options'] = 'nosniff'
        return response
    def destroy(self, request, pk=None):
        delete_photo(self.get_object())
        return Response(status=204)

RANGE = re.compile(r'^bytes=(\d+-\d*|-\d+)$')

@require_GET
def stream(request, pk):
    """Play a video: authorised by the signed link from PhotoSerializer.stream_url (a <video> can't
    send the API token) and supports Range requests so browsers can seek and stream."""
    if not valid_stream_signature(pk, request.GET.get('sig')):
        return HttpResponseForbidden()
    photo = get_object_or_404(Photo, pk=pk, content_type__startswith='video/')
    byte_range = request.headers.get('Range', '')
    try:
        obj = read_range(photo, byte_range if RANGE.match(byte_range) else None)
    except ClientError as error:
        if error.response.get('Error', {}).get('Code') == 'InvalidRange':
            return HttpResponse(status=416)
        raise
    partial = 'ContentRange' in obj
    response = StreamingHttpResponse(obj['Body'].iter_chunks(256 * 1024), status=206 if partial else 200, content_type=photo.content_type)
    response['Content-Length'] = obj['ContentLength']
    if partial:
        response['Content-Range'] = obj['ContentRange']
    response['Accept-Ranges'] = 'bytes'
    response['Cache-Control'] = 'private, max-age=3600'
    response['X-Content-Type-Options'] = 'nosniff'
    return response
