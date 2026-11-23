import time
import uuid
import boto3
from botocore.config import Config
from django.conf import settings
from django.core import signing
from django.utils.crypto import constant_time_compare
from django.db import transaction
from rest_framework.exceptions import ValidationError
from django.shortcuts import get_object_or_404
from common.services import couple_for
from memories.models import Memory
from photos.models import Photo

def storage():
    return boto3.client('s3', endpoint_url=settings.MINIO_ENDPOINT, aws_access_key_id=settings.MINIO_ACCESS_KEY, aws_secret_access_key=settings.MINIO_SECRET_KEY, region_name=settings.MINIO_REGION, config=Config(signature_version='s3v4'))
EXTENSIONS = {'image/jpeg': 'jpg', 'image/png': 'png', 'image/webp': 'webp', 'video/mp4': 'mp4', 'video/quicktime': 'mov', 'video/webm': 'webm'}

def object_key(memory, content_type):
    """{jar id}/{memory id}/{random}.{ext}: grouped per jar and memory; the random name lets a memory hold many photos."""
    return f'{memory.jar_id}/{memory.pk}/{uuid.uuid4().hex}.{EXTENSIONS[content_type]}'

def upload_photo(user, memory_id, upload):
    memory = get_object_or_404(Memory, pk=memory_id, jar__cabinet__couple=couple_for(user))
    key = object_key(memory, upload.content_type)
    client = storage()
    client.upload_fileobj(upload, settings.MINIO_BUCKET, key, ExtraArgs={'ContentType': upload.content_type})
    try:
        return Photo.objects.create(memory=memory, object_key=key, content_type=upload.content_type)
    except Exception:
        client.delete_object(Bucket=settings.MINIO_BUCKET, Key=key)
        raise

STAGE_SALT = 'photos.stage'
STAGE_MAX_AGE = 24 * 3600

def stage_photo(user, upload):
    """Upload a photo before its memory exists (so a memory is only created once all its
    photos are uploaded). Returns a signed token naming the staged object."""
    couple_for(user)
    key = f'staging/{user.pk}/{uuid.uuid4().hex}.{EXTENSIONS[upload.content_type]}'
    storage().upload_fileobj(upload, settings.MINIO_BUCKET, key, ExtraArgs={'ContentType': upload.content_type})
    return signing.dumps({'key': key, 'type': upload.content_type, 'user': user.pk}, salt=STAGE_SALT)

def read_staged(token, user):
    try:
        data = signing.loads(token, salt=STAGE_SALT, max_age=STAGE_MAX_AGE)
    except signing.BadSignature:  # includes SignatureExpired
        raise ValidationError('Ảnh tải lên đã hết hạn, vui lòng chọn lại ảnh.')
    if data.get('user') != user.pk or data.get('type') not in EXTENSIONS:
        raise ValidationError('Ảnh tải lên không hợp lệ.')
    return data

def attach_staged(memory, staged):
    """Move staged objects to {jar id}/{memory id}/… and create their Photo rows. Call inside
    the transaction that saves the memory: on failure the copies are removed and it rolls back."""
    client = storage()
    copied = []
    try:
        for item in staged:
            key = object_key(memory, item['type'])
            client.copy_object(Bucket=settings.MINIO_BUCKET, Key=key, CopySource={'Bucket': settings.MINIO_BUCKET, 'Key': item['key']})
            copied.append(key)
            Photo.objects.create(memory=memory, object_key=key, content_type=item['type'])
    except Exception:
        for key in copied:
            client.delete_object(Bucket=settings.MINIO_BUCKET, Key=key)
        raise
    def remove_staged():
        for item in staged:
            client.delete_object(Bucket=settings.MINIO_BUCKET, Key=item['key'])
    transaction.on_commit(remove_staged)

def relocate_photos(memory):
    """After a memory moves to another jar, move its objects so keys stay {jar id}/{memory id}/…."""
    prefix = f'{memory.jar_id}/{memory.pk}/'
    photos = [p for p in memory.photos.all() if not p.object_key.startswith(prefix)]
    if not photos:
        return
    client = storage()
    for photo in photos:
        old = photo.object_key
        photo.object_key = prefix + old.rsplit('/', 1)[-1]
        client.copy_object(Bucket=settings.MINIO_BUCKET, Key=photo.object_key, CopySource={'Bucket': settings.MINIO_BUCKET, 'Key': old})
        photo.save(update_fields=['object_key'])
        client.delete_object(Bucket=settings.MINIO_BUCKET, Key=old)

# Videos play from a plain <video src>, which can't send the Authorization header, so each video
# gets a signed link. The signature covers the photo id and a 6-hour window (stable within the
# window, so the URL doesn't change on every refresh) and is accepted for the next window too.
STREAM_SALT = 'photos.stream'
STREAM_WINDOW = 6 * 3600

def _stream_signature(pk, offset=0):
    window = int(time.time() // STREAM_WINDOW) - offset
    return signing.Signer(salt=STREAM_SALT).signature(f'{pk}:{window}')

def stream_url(photo):
    return f'/api/photos/{photo.pk}/stream/?sig={_stream_signature(photo.pk)}'

def valid_stream_signature(pk, sig):
    return any(constant_time_compare(sig or '', _stream_signature(pk, offset)) for offset in (0, 1))

def read_range(photo, byte_range=None):
    """The object (or one byte range of it, e.g. 'bytes=0-1023') as an S3 get_object response."""
    extra = {'Range': byte_range} if byte_range else {}
    return storage().get_object(Bucket=settings.MINIO_BUCKET, Key=photo.object_key, **extra)

def read_photo(photo):
    return storage().get_object(Bucket=settings.MINIO_BUCKET, Key=photo.object_key)['Body']

def delete_photo(photo):
    storage().delete_object(Bucket=settings.MINIO_BUCKET, Key=photo.object_key)
    photo.delete()
