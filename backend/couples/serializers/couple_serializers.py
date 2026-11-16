from rest_framework import serializers
from users.serializers.user_serializers import UserSerializer
from couples.models import Couple
class CoupleSerializer(serializers.ModelSerializer):
    members = serializers.SerializerMethodField()
    memory_count = serializers.SerializerMethodField()
    def get_members(self, obj):
        return UserSerializer([m.user for m in obj.memberships.select_related('user')], many=True).data
    def get_memory_count(self, obj):
        from memories.models import Memory
        return Memory.objects.filter(jar__cabinet__couple=obj).count()
    class Meta:
        model = Couple
        fields = ['id', 'name', 'anniversary', 'pet_name', 'pet_type', 'members', 'memory_count']
