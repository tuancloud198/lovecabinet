"""Profile pictures: any photo (JPEG/PNG/WebP/HEIC) cropped to a centered square, stored privately in
S3 as a 512 px JPEG under avatars/{user id}/. Only the user and their partner can load it."""
import io
import uuid
import warnings
from django.conf import settings
from PIL import Image, ImageOps, UnidentifiedImageError
from pillow_heif import register_heif_opener
from rest_framework.exceptions import ValidationError

register_heif_opener()
MAX_MB = 30
SIZE = 512


def square_jpeg(upload):
    if upload.size > MAX_MB * 1024 * 1024:
        raise ValidationError(f'Chọn ảnh tối đa {MAX_MB} MB.')
    try:
        with warnings.catch_warnings():
            warnings.simplefilter('error', Image.DecompressionBombWarning)
            with Image.open(upload) as image:
                image = ImageOps.exif_transpose(image).convert('RGB')
                image = ImageOps.fit(image, (SIZE, SIZE), Image.Resampling.LANCZOS)  # center crop
    except (UnidentifiedImageError, OSError, ValueError, Image.DecompressionBombWarning, Image.DecompressionBombError):
        raise ValidationError('Chỉ hỗ trợ ảnh JPEG, PNG, WebP, HEIC/HEIF hợp lệ.')
    buffer = io.BytesIO()
    image.save(buffer, 'JPEG', quality=88)  # re-encoded: no metadata (GPS) kept
    buffer.seek(0)
    return buffer


def avatar_url(user):
    # The key's random name doubles as a version, so a new picture gets a new (cacheable) URL.
    return f'/api/users/{user.pk}/avatar/?v={user.avatar_key.rsplit("/", 1)[-1].split(".")[0]}' if user.avatar_key else None


def set_avatar(user, upload):
    from photos.services import storage
    data = square_jpeg(upload)
    key = f'avatars/{user.pk}/{uuid.uuid4().hex}.jpg'
    client = storage()
    client.upload_fileobj(data, settings.MINIO_BUCKET, key, ExtraArgs={'ContentType': 'image/jpeg'})
    old, user.avatar_key = user.avatar_key, key
    user.save(update_fields=['avatar_key'])
    if old:
        client.delete_object(Bucket=settings.MINIO_BUCKET, Key=old)


def remove_avatar(user):
    from photos.services import storage
    if user.avatar_key:
        storage().delete_object(Bucket=settings.MINIO_BUCKET, Key=user.avatar_key)
        user.avatar_key = ''
        user.save(update_fields=['avatar_key'])


def can_see(viewer, owner):
    """Yourself and your partner."""
    if viewer.pk == owner.pk:
        return True
    from couples.models import Membership
    mine = Membership.objects.filter(user=viewer).values_list('couple_id', flat=True).first()
    return mine is not None and Membership.objects.filter(user=owner, couple_id=mine).exists()


def read_avatar(user):
    from photos.services import storage
    return storage().get_object(Bucket=settings.MINIO_BUCKET, Key=user.avatar_key)['Body']
