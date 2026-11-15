from rest_framework import serializers
from photos.serializers import PhotoSerializer
from ..models import Memory, Comment
class CommentSerializer(serializers.ModelSerializer):
    author_name = serializers.CharField(source='author.display_name', read_only=True)
    class Meta:
        model = Comment
        fields = ['id', 'text', 'author_name', 'created_at']
class MemorySerializer(serializers.ModelSerializer):
    photos = PhotoSerializer(many=True, read_only=True)
    comments = CommentSerializer(many=True, read_only=True)
    likes = serializers.IntegerField(source='reactions.count', read_only=True)
    liked = serializers.SerializerMethodField()
    author_name = serializers.CharField(source='author.display_name', read_only=True)
    def get_liked(self, obj):
        return obj.reactions.filter(author=self.context['request'].user).exists()
    class Meta:
        model = Memory
        fields = ['id', 'jar', 'title', 'story', 'date', 'emoji', 'author_name', 'photos', 'comments', 'likes', 'liked']
