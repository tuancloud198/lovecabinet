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
    def get_liked(self, obj):
        return obj.reactions.filter(author=self.context['request'].user).exists()
    class Meta:
        model = Memory
        fields = ['id', 'jar', 'title', 'story', 'date', 'emoji', 'author', 'author_name', 'created_at', 'photos', 'comments', 'likes', 'liked']
        read_only_fields = ['author', 'created_at']
