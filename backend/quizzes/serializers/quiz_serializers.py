from rest_framework import serializers
from quizzes.models import Question


class QuestionSerializer(serializers.ModelSerializer):
    author_name = serializers.CharField(source='author.display_name', read_only=True)
    answer = serializers.SerializerMethodField()
    choices = serializers.ListField(child=serializers.CharField(max_length=100, trim_whitespace=True), min_length=2, max_length=4)
    correct = serializers.IntegerField(min_value=0)

    class Meta:
        model = Question
        fields = ['id', 'author', 'author_name', 'text', 'choices', 'correct', 'answer', 'created_at']
        read_only_fields = ['author', 'created_at']

    def validate_choices(self, choices):
        if len({c.casefold() for c in choices}) != len(choices):
            raise serializers.ValidationError('Các lựa chọn không được trùng nhau.')
        return choices

    def validate(self, attrs):
        if attrs['correct'] >= len(attrs['choices']):
            raise serializers.ValidationError('Hãy chọn đáp án đúng.')
        return attrs

    def get_answer(self, obj):
        answer = getattr(obj, 'answer', None)
        if answer is None:
            return None
        return {'user': answer.user_id, 'choice': answer.choice, 'correct': answer.is_correct, 'answered_on': answer.answered_on, 'created_at': answer.created_at}

    def to_representation(self, obj):
        data = super().to_representation(obj)
        # The partner only learns the right answer after answering.
        if obj.author_id != self.context['request'].user.id and not hasattr(obj, 'answer'):
            data['correct'] = None
        return data
