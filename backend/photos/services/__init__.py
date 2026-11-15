import uuid
import boto3
from botocore.config import Config
from django.conf import settings
from django.shortcuts import get_object_or_404
from common.services import couple_for
from memories.models import Memory
from ..models import Photo

def storage():
    return boto3.client('s3', endpoint_url=settings.MINIO_ENDPOINT, aws_access_key_id=settings.MINIO_ACCESS_KEY, aws_secret_access_key=settings.MINIO_SECRET_KEY, region_name='us-east-1', config=Config(signature_version='s3v4'))
def upload_photo(user, memory_id, upload):
    memory = get_object_or_404(Memory, pk=memory_id, jar__cabinet__couple=couple_for(user))
    key = f'{memory.jar.cabinet.couple_id}/{uuid.uuid4().hex}'
    client = storage()
    client.upload_fileobj(upload, settings.MINIO_BUCKET, key, ExtraArgs={'ContentType': upload.content_type})
    try:
        return Photo.objects.create(memory=memory, object_key=key, content_type=upload.content_type)
    except Exception:
        client.delete_object(Bucket=settings.MINIO_BUCKET, Key=key)
        raise

def read_photo(photo):
    return storage().get_object(Bucket=settings.MINIO_BUCKET, Key=photo.object_key)['Body']

def delete_photo(photo):
    storage().delete_object(Bucket=settings.MINIO_BUCKET, Key=photo.object_key)
    photo.delete()
