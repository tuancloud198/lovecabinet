import io
import json
import time
import urllib.parse
import urllib.request
from django.conf import settings
from django.core.management.base import BaseCommand
from PIL import Image
from memories.models import Memory
from photos.services import storage

GPS_IFD = 0x8825
HEAD_BYTES = 256 * 1024  # EXIF sits at the start of a JPEG


def to_degrees(value, ref):
    degrees, minutes, seconds = (float(v) for v in value)
    result = degrees + minutes / 60 + seconds / 3600
    return -result if ref in ('S', 'W') else result


def gps_from_jpeg(data):
    """(latitude, longitude) from a photo's EXIF, or None."""
    try:
        gps = Image.open(io.BytesIO(data)).getexif().get_ifd(GPS_IFD)
        lat, lon = to_degrees(gps[2], gps.get(1, 'N')), to_degrees(gps[4], gps.get(3, 'E'))
    except Exception:  # no/partial EXIF, not an image
        return None
    if not (-90 <= lat <= 90 and -180 <= lon <= 180) or (lat == 0 and lon == 0):
        return None
    return round(lat, 6), round(lon, 6)


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
    help = "Pin memories that have no location yet using the GPS in their photos' EXIF."

    def add_arguments(self, parser):
        parser.add_argument('--geocode', action='store_true', help='also look up place names (OpenStreetMap Nominatim, 1 request/s)')
        parser.add_argument('--dry-run', action='store_true')

    def handle(self, *args, geocode=False, dry_run=False, **options):
        client = storage()
        pinned = 0
        memories = Memory.objects.filter(latitude__isnull=True).prefetch_related('photos').order_by('id')
        for memory in memories:
            for photo in sorted(memory.photos.all(), key=lambda p: p.id):  # first photo with GPS wins, like the app
                if not photo.content_type.startswith('image/'):
                    continue
                data = client.get_object(Bucket=settings.MINIO_BUCKET, Key=photo.object_key, Range=f'bytes=0-{HEAD_BYTES - 1}')['Body'].read()
                coords = gps_from_jpeg(data)
                if coords:
                    break
            else:
                continue
            memory.latitude, memory.longitude = coords
            if geocode:
                memory.place = place_name(*coords)
                time.sleep(1.1)  # Nominatim usage policy: at most 1 request per second
            pinned += 1
            self.stdout.write(f'memory {memory.pk}: pinned from photo {photo.pk}' + (f' ({memory.place})' if memory.place else ''))
            if not dry_run:
                memory.save(update_fields=['latitude', 'longitude', 'place'])
        self.stdout.write(self.style.SUCCESS(f'{pinned} memories pinned' + (' (dry run, nothing saved)' if dry_run else '')))
