import io
import logging
import warnings
from django.core.files.uploadedfile import InMemoryUploadedFile
from PIL import Image, ImageOps, UnidentifiedImageError
from pillow_heif import register_heif_opener
from rest_framework import serializers
from photos.models import Photo

logger = logging.getLogger(__name__)
register_heif_opener()  # lets Pillow read HEIC/HEIF (iPhone photos)
MAX_UPLOAD_MB = 80  # full-size phone photos (HEIF, 48 MP, ProRAW-derived) can be large; browsers usually shrink them first
MAX_VIDEO_MB = 200
MAX_SIDE = 4096  # long edge of a converted HEIF photo
FORMATS = {'JPEG': 'image/jpeg', 'PNG': 'image/png', 'WEBP': 'image/webp'}

# ISO-BMFF brands that are still images (HEIF/AVIF); any other `ftyp` file is treated as MP4/MOV video.
IMAGE_BRANDS = {b'heic', b'heix', b'heim', b'heis', b'hevc', b'hevx', b'mif1', b'msf1', b'avif', b'avis', b'crx '}

def video_type(header):
    """Content type of a video from its first bytes, or None if it isn't MP4, MOV or WebM."""
    if header[4:8] == b'ftyp':
        brand = header[8:12]
        if brand in IMAGE_BRANDS:
            return None
        return 'video/quicktime' if brand == b'qt  ' else 'video/mp4'
    if header[4:8] in (b'moov', b'mdat', b'wide', b'free', b'skip'):  # older QuickTime files without ftyp
        return 'video/quicktime'
    if header[:4] == b'\x1a\x45\xdf\xa3':  # EBML: WebM/Matroska
        return 'video/webm'
    return None

class PhotoSerializer(serializers.ModelSerializer):
    """A photo or video of a memory. Videos are played from `stream_url` (signed, supports seeking)."""
    url = serializers.SerializerMethodField()
    kind = serializers.SerializerMethodField()
    stream_url = serializers.SerializerMethodField()
    def get_url(self, obj):
        return f'/api/photos/{obj.pk}/content/'
    def get_kind(self, obj):
        return 'video' if obj.content_type.startswith('video/') else 'image'
    def get_stream_url(self, obj):
        from photos.services import stream_url
        return stream_url(obj) if obj.content_type.startswith('video/') else None
    class Meta:
        model = Photo
        fields = ['id', 'memory', 'url', 'kind', 'stream_url']

def heif_to_jpeg(upload):
    """Most browsers can't display HEIC/HEIF, so store those photos as JPEG instead."""
    upload.seek(0)
    with Image.open(upload) as image:
        image = ImageOps.exif_transpose(image).convert('RGB')
        image.thumbnail((MAX_SIDE, MAX_SIDE), Image.Resampling.LANCZOS)
        buffer = io.BytesIO()
        image.save(buffer, 'JPEG', quality=88)
    name = (upload.name or 'photo').rsplit('.', 1)[0] + '.jpg'
    return InMemoryUploadedFile(buffer, 'file', name, 'image/jpeg', buffer.getbuffer().nbytes, None)

class StageSerializer(serializers.Serializer):
    file = serializers.FileField()
    def validate_file(self, upload):
        header = upload.read(32)  # file signature: picks video vs image, logged when rejected
        upload.seek(0)
        kind = video_type(header)
        if kind:  # stored as-is; served with a fixed content type and nosniff
            if upload.size > MAX_VIDEO_MB * 1024 * 1024:
                raise serializers.ValidationError(f'Chọn video tối đa {MAX_VIDEO_MB} MB.')
            upload.content_type = kind
            return upload
        if upload.size > MAX_UPLOAD_MB * 1024 * 1024:
            raise serializers.ValidationError(f'Chọn ảnh tối đa {MAX_UPLOAD_MB} MB.')
        try:
            with warnings.catch_warnings():
                warnings.simplefilter('error', Image.DecompressionBombWarning)
                image = Image.open(upload)
                image.verify()
                if image.format == 'HEIF':
                    upload = heif_to_jpeg(upload)
                else:
                    upload.content_type = FORMATS[image.format]
        except (UnidentifiedImageError, OSError, KeyError, ValueError, Image.DecompressionBombWarning, Image.DecompressionBombError) as error:
            logger.warning('Photo rejected: %r (name=%r, type=%r, size=%s, head=%r)', error, upload.name, upload.content_type, upload.size, header)
            raise serializers.ValidationError('Chỉ hỗ trợ ảnh JPEG, PNG, WebP, HEIC/HEIF và video MP4, MOV, WebM hợp lệ.')
        upload.seek(0)
        return upload

class UploadSerializer(StageSerializer):
    memory = serializers.IntegerField(min_value=1)
