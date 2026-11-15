import time
from botocore.exceptions import BotoCoreError, ClientError
from django.conf import settings
from django.core.management.base import BaseCommand, CommandError
from photos.services import storage

class Command(BaseCommand):
    help = 'Wait for MinIO and ensure the private memory bucket exists.'
    def handle(self, *args, **options):
        client = storage()
        for attempt in range(30):
            try:
                try:
                    client.head_bucket(Bucket=settings.MINIO_BUCKET)
                except ClientError as exc:
                    if str(exc.response['Error']['Code']) not in ['404', 'NoSuchBucket']:
                        raise
                    try:
                        client.create_bucket(Bucket=settings.MINIO_BUCKET)
                    except ClientError as create_exc:
                        if create_exc.response['Error']['Code'] not in ['BucketAlreadyOwnedByYou', 'BucketAlreadyExists']:
                            raise
                self.stdout.write(self.style.SUCCESS('Private storage bucket is ready.'))
                return
            except (BotoCoreError, ClientError) as exc:
                if attempt == 29:
                    raise CommandError(f'Storage initialization failed: {exc}')
                time.sleep(2)
