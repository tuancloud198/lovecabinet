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
FORMATS = {'JPEG': 'image/jpeg', 'PNG': 'image/png', 'WEBP': 'image/webp'}

class PhotoSerializer(serializers.ModelSerializer):
    url = serializers.SerializerMethodField()
    def get_url(self, obj):
        return f'/api/photos/{obj.pk}/content/'
    class Meta:
        model = Photo
        fields = ['id', 'memory', 'url']

def heif_to_jpeg(upload):
    """Most browsers can't display HEIC/HEIF, so store those photos as JPEG instead."""
    upload.seek(0)
    with Image.open(upload) as image:
        image = ImageOps.exif_transpose(image).convert('RGB')
        buffer = io.BytesIO()
        image.save(buffer, 'JPEG', quality=90)
    name = (upload.name or 'photo').rsplit('.', 1)[0] + '.jpg'
    return InMemoryUploadedFile(buffer, 'file', name, 'image/jpeg', buffer.getbuffer().nbytes, None)

class UploadSerializer(serializers.Serializer):
    memory = serializers.IntegerField(min_value=1)
    file = serializers.FileField()
    def validate_file(self, upload):
        if upload.size > 10 * 1024 * 1024:
            raise serializers.ValidationError('Chọn ảnh tối đa 10 MB.')
        header = upload.read(32)  # file signature, logged when the photo is rejected
        upload.seek(0)
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
            raise serializers.ValidationError('Chỉ hỗ trợ ảnh JPEG, PNG, WebP và HEIC/HEIF hợp lệ.')
        upload.seek(0)
        return upload
