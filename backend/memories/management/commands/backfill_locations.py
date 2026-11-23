import json
import time
import urllib.parse
import urllib.request
from django.conf import settings
from django.core.management.base import BaseCommand
from memories.models import Memory
from photos.gps import gps_from_bytes
from photos.models import Photo
from photos.services import storage

HEAD_BYTES = 256 * 1024  # EXIF sits at the start of a JPEG


def place_name(lat, lon):
    """Short place name from OpenStreetMap Nominatim (same format as the app), or ''."""
    query = urllib.parse.urlencode({'format': 'jsonv2', 'lat': lat, 'lon': lon, 'zoom': 16, 'accept-language': 'vi'})
    request = urllib.request.Request(f'https://nominatim.openstreetmap.org/reverse?{query}', headers={'User-Agent': 'memory-map-backfill/1.0'})
    try:
        with urllib.request.urlopen(request, timeout=10) as response:
            data = json.load(response)
    except Exception:
        return ''
    address = data.get('address', {})
    area = next((address[k] for k in ('city', 'town', 'village', 'county', 'state') if address.get(k)), '')
    name = data.get('name') or address.get('road') or ''
    return ', '.join(dict.fromkeys(p for p in (name, area) if p))[:120]


class Command(BaseCommand):
    help = ("Read the GPS of photos that have no location yet from their EXIF (in S3), and pin memories "
            "without a location at their first photo with GPS.")

    def add_arguments(self, parser):
        parser.add_argument('--geocode', action='store_true', help='also look up place names (OpenStreetMap Nominatim, 1 request/s, one per ~100 m spot)')
        parser.add_argument('--dry-run', action='store_true')

    def handle(self, *args, geocode=False, dry_run=False, **options):
        client = storage()
        names = {}  # ~100 m spot -> name, so nearby photos share one lookup

        def name_for(lat, lon):
            if not geocode:
                return ''
            spot = (round(lat, 3), round(lon, 3))
            if spot not in names:
                names[spot] = place_name(lat, lon)
                time.sleep(1.1)  # Nominatim usage policy: at most 1 request per second
            return names[spot]

        located = 0
        for photo in Photo.objects.filter(latitude__isnull=True, content_type__startswith='image/').order_by('id'):
            data = client.get_object(Bucket=settings.MINIO_BUCKET, Key=photo.object_key, Range=f'bytes=0-{HEAD_BYTES - 1}')['Body'].read()
            coords = gps_from_bytes(data)
            if not coords:
                continue
            photo.latitude, photo.longitude = coords
            photo.place = name_for(*coords)
            located += 1
            self.stdout.write(f'photo {photo.pk} (memory {photo.memory_id}): located' + (f' ({photo.place})' if photo.place else ''))
            if not dry_run:
                photo.save(update_fields=['latitude', 'longitude', 'place'])

        pinned = 0
        for memory in Memory.objects.filter(latitude__isnull=True).prefetch_related('photos').order_by('id'):
            first = next((p for p in sorted(memory.photos.all(), key=lambda p: p.id) if p.latitude is not None), None)
            if not first:
                continue
            memory.latitude, memory.longitude, memory.place = first.latitude, first.longitude, first.place or name_for(first.latitude, first.longitude)
            pinned += 1
            self.stdout.write(f'memory {memory.pk}: pinned from photo {first.pk}' + (f' ({memory.place})' if memory.place else ''))
            if not dry_run:
                memory.save(update_fields=['latitude', 'longitude', 'place'])
        self.stdout.write(self.style.SUCCESS(f'{located} photos located, {pinned} memories pinned' + (' (dry run, nothing saved)' if dry_run else '')))
