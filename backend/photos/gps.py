"""GPS position from a photo's EXIF (JPEG, HEIC via pillow-heif, PNG/WebP with EXIF)."""
import io
from PIL import Image

GPS_IFD = 0x8825


def _degrees(value, ref):
    degrees, minutes, seconds = (float(v) for v in value)
    result = degrees + minutes / 60 + seconds / 3600
    return -result if ref in ('S', 'W') else result


def gps_of_image(image):
    """(latitude, longitude) rounded to 6 decimals, or None."""
    try:
        gps = image.getexif().get_ifd(GPS_IFD)
        lat, lon = _degrees(gps[2], gps.get(1, 'N')), _degrees(gps[4], gps.get(3, 'E'))
    except Exception:  # no/partial EXIF
        return None
    if not (-90 <= lat <= 90 and -180 <= lon <= 180) or (lat == 0 and lon == 0):
        return None
    return round(lat, 6), round(lon, 6)


def gps_from_bytes(data):
    try:
        with Image.open(io.BytesIO(data)) as image:
            return gps_of_image(image)
    except Exception:
        return None
