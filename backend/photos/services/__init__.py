import io
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

# ---- Photo sizes: the original plus smaller JPEG copies, so lists and the memory page don't download
# multi-MB originals. Copies sit next to the original: {jar}/{memory}/{name}.thumb.jpg / .display.jpg.
VARIANTS = {'thumb': 400, 'display': 1600}  # long edge in px

def variant_key(key, name):
    return key.rsplit('.', 1)[0] + f'.{name}.jpg'

def object_keys(photo):
    """Every S3 object of a photo: the original and its smaller copies."""
    return [photo.object_key] + ([variant_key(photo.object_key, name) for name in VARIANTS] if photo.variants else [])

def make_variants(fileobj):
    """{name: JPEG bytes} for an image file (EXIF rotation applied, transparency on white)."""
    from PIL import Image, ImageOps
    fileobj.seek(0)
    with Image.open(fileobj) as image:
        image = ImageOps.exif_transpose(image)
        if image.mode in ('RGBA', 'LA', 'P'):
            image = image.convert('RGBA')
            background = Image.new('RGB', image.size, 'white')
            background.paste(image, mask=image.getchannel('A'))
            image = background
        else:
            image = image.convert('RGB')
        variants = {}
        for name, side in VARIANTS.items():
            copy = image.copy()
            copy.thumbnail((side, side), Image.Resampling.LANCZOS)
            buffer = io.BytesIO()
            copy.save(buffer, 'JPEG', quality=82, optimize=True, progressive=True)
            variants[name] = buffer.getvalue()
    fileobj.seek(0)
    return variants

def put_object(client, key, fileobj, content_type):
    client.upload_fileobj(fileobj, settings.MINIO_BUCKET, key, ExtraArgs={'ContentType': content_type})

def upload_with_variants(client, key, upload):
    """Upload a file and, for images, its smaller copies. Returns whether copies were made."""
    variants = make_variants(upload) if upload.content_type.startswith('image/') else {}
    put_object(client, key, upload, upload.content_type)
    for name, data in variants.items():
        put_object(client, variant_key(key, name), io.BytesIO(data), 'image/jpeg')
    return bool(variants)

EXTENSIONS = {'image/jpeg': 'jpg', 'image/png': 'png', 'image/webp': 'webp', 'video/mp4': 'mp4', 'video/quicktime': 'mov', 'video/webm': 'webm'}

def memory_prefix(memory):
    """media/c{couple id}/{jar id}/{memory id}/: everything of a couple under one folder, so the CDN cookie
    can allow exactly that folder (photos/cdn.py)."""
    return f'media/c{memory.jar.cabinet.couple_id}/{memory.jar_id}/{memory.pk}/'

def object_key(memory, content_type):
    """{memory prefix}{random}.{ext}: the random name lets a memory hold many photos and can't be guessed."""
    return f'{memory_prefix(memory)}{uuid.uuid4().hex}.{EXTENSIONS[content_type]}'

NO_LOCATION = {'latitude': None, 'longitude': None, 'place': ''}

def upload_photo(user, memory_id, upload, location=NO_LOCATION):
    memory = get_object_or_404(Memory, pk=memory_id, jar__cabinet__couple=couple_for(user))
    key = object_key(memory, upload.content_type)
    client = storage()
    variants = upload_with_variants(client, key, upload)
    try:
        return Photo.objects.create(memory=memory, object_key=key, content_type=upload.content_type, variants=variants, **location)
    except Exception:
        for k in [key] + ([variant_key(key, name) for name in VARIANTS] if variants else []):
            client.delete_object(Bucket=settings.MINIO_BUCKET, Key=k)
        raise

STAGE_SALT = 'photos.stage'
STAGE_MAX_AGE = 24 * 3600

def stage_photo(user, upload, location=NO_LOCATION):
    """Upload a photo before its memory exists (so a memory is only created once all its
    photos are uploaded). Returns a signed token naming the staged object."""
    couple_for(user)
    key = f'staging/{user.pk}/{uuid.uuid4().hex}.{EXTENSIONS[upload.content_type]}'
    variants = upload_with_variants(storage(), key, upload)
    return signing.dumps({'key': key, 'type': upload.content_type, 'user': user.pk, 'location': location, 'variants': variants}, salt=STAGE_SALT)

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
            pairs = [(item['key'], key)] + [(variant_key(item['key'], name), variant_key(key, name)) for name in VARIANTS if item.get('variants')]
            for source, target in pairs:
                client.copy_object(Bucket=settings.MINIO_BUCKET, Key=target, CopySource={'Bucket': settings.MINIO_BUCKET, 'Key': source})
                copied.append(target)
            Photo.objects.create(memory=memory, object_key=key, content_type=item['type'], variants=bool(item.get('variants')), **(item.get('location') or NO_LOCATION))
    except Exception:
        for key in copied:
            client.delete_object(Bucket=settings.MINIO_BUCKET, Key=key)
        raise
    def remove_staged():
        for item in staged:
            for key in [item['key']] + [variant_key(item['key'], name) for name in VARIANTS if item.get('variants')]:
                client.delete_object(Bucket=settings.MINIO_BUCKET, Key=key)
    transaction.on_commit(remove_staged)

def relocate_photos(memory):
    """After a memory moves to another jar (or for keys from an older layout), move its objects so keys
    stay {memory prefix}…. Each photo is copied, saved, then the old objects removed: safe while in use."""
    prefix = memory_prefix(memory)
    photos = [p for p in memory.photos.all() if not p.object_key.startswith(prefix)]
    if not photos:
        return
    client = storage()
    for photo in photos:
        old_keys = object_keys(photo)
        photo.object_key = prefix + photo.object_key.rsplit('/', 1)[-1]
        for old, new in zip(old_keys, object_keys(photo)):
            client.copy_object(Bucket=settings.MINIO_BUCKET, Key=new, CopySource={'Bucket': settings.MINIO_BUCKET, 'Key': old})
        photo.save(update_fields=['object_key'])
        for old in old_keys:
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
    from photos import cdn
    return cdn.url(photo.object_key) or f'/api/photos/{photo.pk}/stream/?sig={_stream_signature(photo.pk)}'

def valid_stream_signature(pk, sig):
    return any(constant_time_compare(sig or '', _stream_signature(pk, offset)) for offset in (0, 1))

def read_range(photo, byte_range=None):
    """The object (or one byte range of it, e.g. 'bytes=0-1023') as an S3 get_object response."""
    extra = {'Range': byte_range} if byte_range else {}
    return storage().get_object(Bucket=settings.MINIO_BUCKET, Key=photo.object_key, **extra)

def read_photo(photo, size=None):
    """The original, or a smaller copy ('thumb' / 'display') when it has one. Returns (body, content type)."""
    if size in VARIANTS and photo.variants:
        return storage().get_object(Bucket=settings.MINIO_BUCKET, Key=variant_key(photo.object_key, size))['Body'], 'image/jpeg'
    return storage().get_object(Bucket=settings.MINIO_BUCKET, Key=photo.object_key)['Body'], photo.content_type

def delete_photo(photo):
    client = storage()
    for key in object_keys(photo):
        client.delete_object(Bucket=settings.MINIO_BUCKET, Key=key)
    photo.delete()
