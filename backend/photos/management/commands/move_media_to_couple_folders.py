"""Move photos/videos stored under the old {jar}/{memory}/… layout to media/c{couple}/{jar}/{memory}/…, so
the CDN cookie (photos/cdn.py) can cover them. Each photo is copied, saved, then the old objects removed, so
it's safe to run while the app is in use, and to re-run (moved photos are skipped).

    python manage.py move_media_to_couple_folders [--dry-run]
"""
from django.core.management.base import BaseCommand
from memories.models import Memory
from photos.services import memory_prefix, object_keys, relocate_photos

class Command(BaseCommand):
    help = 'Move photo/video objects to media/c<couple>/<jar>/<memory>/ keys.'

    def add_arguments(self, parser):
        parser.add_argument('--dry-run', action='store_true', help='Only count what would move.')

    def handle(self, *args, dry_run=False, **options):
        photos = objects = 0
        for memory in Memory.objects.select_related('jar__cabinet').prefetch_related('photos').order_by('pk'):
            prefix = memory_prefix(memory)
            pending = [p for p in memory.photos.all() if not p.object_key.startswith(prefix)]
            if not pending:
                continue
            photos += len(pending)
            objects += sum(len(object_keys(p)) for p in pending)
            if not dry_run:
                relocate_photos(memory)
        verb = 'Would move' if dry_run else 'Moved'
        self.stdout.write(f'{verb} {photos} photos/videos ({objects} objects).')
