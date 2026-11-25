from rest_framework.decorators import action
from rest_framework.exceptions import PermissionDenied, ValidationError
from rest_framework.response import Response
from common.api import ScopedViewSet
from common.services import couple_for
from quizzes.models import Question
from quizzes.serializers.quiz_serializers import QuestionSerializer
from quizzes.services import answer_question, streaks


class QuestionViewSet(ScopedViewSet):
    """Couple quiz: create (author = you), list, answer (the partner, once), delete (author, unanswered only)."""
    queryset = Question.objects.select_related('author', 'answer')
    serializer_class = QuestionSerializer
    scope = 'couple'
    http_method_names = ['get', 'post', 'delete']

    def perform_create(self, serializer):
        serializer.save(couple=couple_for(self.request.user), author=self.request.user)

    def perform_destroy(self, instance):
        if instance.author_id != self.request.user.id:
            raise PermissionDenied('Chỉ người tạo mới xóa được câu hỏi.')
        if hasattr(instance, 'answer'):
            raise ValidationError('Câu đã được trả lời thì không xóa được.')
        instance.delete()

    @action(detail=True, methods=['post'])
    def answer(self, request, pk=None):
        question = self.get_object()
        try:
            choice = int(request.data.get('choice'))
        except (TypeError, ValueError):
            raise ValidationError('Lựa chọn không hợp lệ.')
        answer = answer_question(question, request.user, choice)
        question = self.get_queryset().get(pk=question.pk)
        current, longest = streaks(question.couple)
        return Response({'question': self.get_serializer(question).data, 'points': answer.points, 'streak': current, 'max_streak': longest})
