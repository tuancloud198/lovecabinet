from django.utils import timezone
from rest_framework import serializers
from users.serializers.user_serializers import UserSerializer
from couples.models import Couple
class CoupleSerializer(serializers.ModelSerializer):
    members = serializers.SerializerMethodField()
    memory_count = serializers.SerializerMethodField()
    quiz_streak = serializers.SerializerMethodField()
    quiz_max_streak = serializers.SerializerMethodField()
    points_today = serializers.SerializerMethodField()  # earned today, towards daily_points_limit
    daily_points_limit = serializers.SerializerMethodField()
    def validate_pet_type(self, value):
        # The dog is everyone's; other pets are bought in the shop (item 'pet_<type>'). Growth is shared.
        from shop.models import Purchase
        if value != 'dog' and self.instance and not Purchase.objects.filter(couple=self.instance, item_id=f'pet_{value}').exists():
            raise serializers.ValidationError('Hai bạn chưa có bạn nhỏ này, hãy ghé cửa hàng nhé.')
        return value
    def validate(self, attrs):
        met = attrs.get('met_on', getattr(self.instance, 'met_on', None))
        since = attrs.get('dating_since', getattr(self.instance, 'dating_since', None))
        today = timezone.localdate()
        if any(d and d > today for d in (met, since)):
            raise serializers.ValidationError('Ngày không được ở tương lai.')
        if met and since and since < met:
            raise serializers.ValidationError('Ngày yêu nhau phải sau ngày gặp nhau.')
        return attrs
    def _streaks(self, obj):
        if not hasattr(obj, '_streaks'):
            from quizzes.services import streaks
            obj._streaks = streaks(obj)
        return obj._streaks
    def _today_points(self, obj):
        if not hasattr(obj, '_today_points'):
            from couples.points import today_points
            obj._today_points = today_points(obj)
        return obj._today_points
    def get_points_today(self, obj):
        return self._today_points(obj)[0]
    def get_daily_points_limit(self, obj):
        return self._today_points(obj)[1]
    def get_quiz_streak(self, obj):
        return self._streaks(obj)[0]
    def get_quiz_max_streak(self, obj):
        return self._streaks(obj)[1]
    def get_members(self, obj):
        return UserSerializer([m.user for m in obj.memberships.select_related('user')], many=True).data
    def get_memory_count(self, obj):
        from memories.models import Memory
        return Memory.objects.filter(jar__cabinet__couple=obj).count()
    class Meta:
        model = Couple
        fields = ['id', 'name', 'met_on', 'dating_since', 'pet_name', 'pet_type', 'pet_mood', 'points_earned', 'points_spent', 'points_today', 'daily_points_limit', 'quiz_streak', 'quiz_max_streak', 'members', 'memory_count']
        read_only_fields = ['points_earned', 'points_spent']
