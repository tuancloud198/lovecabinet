from rest_framework import serializers
from photos.serializers.photo_serializers import PhotoSerializer
from memories.models import Memory, Comment
class CommentSerializer(serializers.ModelSerializer):
    author_name = serializers.CharField(source='author.display_name', read_only=True)
    class Meta:
        model = Comment
        fields = ['id', 'text', 'author', 'author_name', 'created_at']
        read_only_fields = ['author']
class MemorySerializer(serializers.ModelSerializer):
    photos = PhotoSerializer(many=True, read_only=True)
    comments = CommentSerializer(many=True, read_only=True)
    likes = serializers.IntegerField(source='reactions.count', read_only=True)
    liked = serializers.SerializerMethodField()
    author_name = serializers.CharField(source='author.display_name', read_only=True)
    staged_photos = serializers.ListField(child=serializers.CharField(max_length=1000), write_only=True, required=False, max_length=30)
    def validate_staged_photos(self, tokens):
        from photos.services import read_staged
        return [read_staged(token, self.context['request'].user) for token in tokens]
    def validate(self, attrs):
        # A location is a latitude/longitude pair; clearing it also clears the place name.
        coords = [attrs.get(f, getattr(self.instance, f, None)) for f in ('latitude', 'longitude')]
        if (coords[0] is None) != (coords[1] is None):
            raise serializers.ValidationError('Vị trí cần cả vĩ độ và kinh độ.')
        if coords[0] is None and ('latitude' in attrs or 'longitude' in attrs):
            attrs['place'] = ''
        return attrs
    def get_liked(self, obj):
        return obj.reactions.filter(author=self.context['request'].user).exists()
    class Meta:
        model = Memory
        fields = ['id', 'jar', 'title', 'story', 'date', 'emoji', 'latitude', 'longitude', 'place', 'author', 'author_name', 'created_at', 'photos', 'comments', 'likes', 'liked', 'staged_photos']
        read_only_fields = ['author', 'created_at']
