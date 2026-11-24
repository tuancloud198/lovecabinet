import io
from django.conf import settings
from django.core.management.base import BaseCommand
from photos.models import Photo
from photos.services import make_variants, put_object, storage, variant_key


class Command(BaseCommand):
    help = 'Create the smaller copies (thumb ~400 px, display ~1600 px) for photos uploaded before they existed.'

    def add_arguments(self, parser):
        parser.add_argument('--dry-run', action='store_true')

    def handle(self, *args, dry_run=False, **options):
        client = storage()
        done = failed = saved = 0
        photos = Photo.objects.filter(variants=False, content_type__startswith='image/').order_by('id')
        self.stdout.write(f'{photos.count()} photos without smaller copies')
        for photo in photos:
            if dry_run:
                continue
            try:
                original = client.get_object(Bucket=settings.MINIO_BUCKET, Key=photo.object_key)['Body'].read()
                variants = make_variants(io.BytesIO(original))
                for name, data in variants.items():
                    put_object(client, variant_key(photo.object_key, name), io.BytesIO(data), 'image/jpeg')
            except Exception as error:  # keep going; the photo keeps loading its original
                failed += 1
                self.stderr.write(f'photo {photo.pk}: {error!r}')
                continue
            photo.variants = True
            photo.save(update_fields=['variants'])
            done += 1
            saved += len(original) - len(variants['display'])
            self.stdout.write(f'photo {photo.pk}: {len(original) // 1024} KB -> display {len(variants["display"]) // 1024} KB, thumb {len(variants["thumb"]) // 1024} KB')
        self.stdout.write(self.style.SUCCESS(f'{done} photos done, {failed} failed' + (' (dry run)' if dry_run else f', ~{saved // 1048576} MB less to download per full view')))
