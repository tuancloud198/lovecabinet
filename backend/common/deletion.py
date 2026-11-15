"""Remove private objects before deleting their owning database records."""
from django.db import transaction
from photos.models import Photo
from photos.services import storage
from django.conf import settings

def delete_with_photos(instance, photo_scope):
    photos = list(Photo.objects.filter(**{photo_scope: instance}))
    if photos:
        client = storage()
        for photo in photos:
            client.delete_object(Bucket=settings.MINIO_BUCKET, Key=photo.object_key)
    with transaction.atomic():
        instance.delete()
