import uuid
import boto3
from botocore.config import Config
from django.conf import settings
from django.shortcuts import get_object_or_404
from common.services import couple_for
from memories.models import Memory
from photos.models import Photo

def storage():
    return boto3.client('s3', endpoint_url=settings.MINIO_ENDPOINT, aws_access_key_id=settings.MINIO_ACCESS_KEY, aws_secret_access_key=settings.MINIO_SECRET_KEY, region_name=settings.MINIO_REGION, config=Config(signature_version='s3v4'))
EXTENSIONS = {'image/jpeg': 'jpg', 'image/png': 'png', 'image/webp': 'webp'}

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

def read_photo(photo):
    return storage().get_object(Bucket=settings.MINIO_BUCKET, Key=photo.object_key)['Body']

def delete_photo(photo):
    storage().delete_object(Bucket=settings.MINIO_BUCKET, Key=photo.object_key)
    photo.delete()
