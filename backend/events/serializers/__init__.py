from rest_framework import serializers
from ..models import Event
class EventSerializer(serializers.ModelSerializer):
    class Meta:
        model = Event
        fields = ['id', 'couple', 'title', 'date', 'emoji']
        read_only_fields = ['couple']
