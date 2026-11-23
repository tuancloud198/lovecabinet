from django.utils import timezone
from rest_framework import serializers
from users.serializers.user_serializers import UserSerializer
from couples.models import Couple
class CoupleSerializer(serializers.ModelSerializer):
    members = serializers.SerializerMethodField()
    memory_count = serializers.SerializerMethodField()
    def validate(self, attrs):
        met = attrs.get('met_on', getattr(self.instance, 'met_on', None))
        since = attrs.get('dating_since', getattr(self.instance, 'dating_since', None))
        today = timezone.localdate()
        if any(d and d > today for d in (met, since)):
            raise serializers.ValidationError('Ngày không được ở tương lai.')
        if met and since and since < met:
            raise serializers.ValidationError('Ngày yêu nhau phải sau ngày gặp nhau.')
        return attrs
    def get_members(self, obj):
        return UserSerializer([m.user for m in obj.memberships.select_related('user')], many=True).data
    def get_memory_count(self, obj):
        from memories.models import Memory
        return Memory.objects.filter(jar__cabinet__couple=obj).count()
    class Meta:
        model = Couple
        fields = ['id', 'name', 'met_on', 'dating_since', 'pet_name', 'pet_type', 'members', 'memory_count']
