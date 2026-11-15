import warnings
from PIL import Image, UnidentifiedImageError
from rest_framework import serializers
from ..models import Photo
class PhotoSerializer(serializers.ModelSerializer):
    url = serializers.SerializerMethodField()
    def get_url(self, obj):
        return f'/api/photos/{obj.pk}/content/'
    class Meta:
        model = Photo
        fields = ['id', 'memory', 'url']
class UploadSerializer(serializers.Serializer):
    memory = serializers.IntegerField(min_value=1)
    file = serializers.FileField()
    def validate_file(self, upload):
        if upload.size > 10 * 1024 * 1024:
            raise serializers.ValidationError('Chọn ảnh tối đa 10 MB.')
        try:
            with warnings.catch_warnings():
                warnings.simplefilter('error', Image.DecompressionBombWarning)
                image = Image.open(upload)
                image.verify()
                upload.content_type = {'JPEG': 'image/jpeg', 'PNG': 'image/png', 'WEBP': 'image/webp'}[image.format]
        except (UnidentifiedImageError, OSError, KeyError, Image.DecompressionBombWarning, Image.DecompressionBombError):
            raise serializers.ValidationError('Chỉ hỗ trợ ảnh JPEG, PNG và WebP hợp lệ.')
        upload.seek(0)
        return upload
