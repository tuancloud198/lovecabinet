from datetime import timedelta
from django.db import IntegrityError, transaction
from django.utils import timezone
from rest_framework.exceptions import PermissionDenied, ValidationError
from couples.models import QUIZ_POINTS
from couples.points import award
from quizzes.models import Answer

POINTS_PER_ANSWER = QUIZ_POINTS


def answer_question(question, user, choice):
    """Record the partner's answer and give the pet its points (once per question)."""
    if question.author_id == user.id:
        raise PermissionDenied('Câu này là của bạn, để người ấy trả lời nhé.')
    if hasattr(question, 'answer'):
        raise ValidationError('Câu này đã được trả lời rồi.')
    if not 0 <= choice < len(question.choices):
        raise ValidationError('Lựa chọn không hợp lệ.')
    try:
        with transaction.atomic():
            answer = Answer.objects.create(question=question, user=user, choice=choice, answered_on=timezone.localdate())
            answer.points = award(question.couple_id, POINTS_PER_ANSWER)  # 0 once the day's limit is reached
    except IntegrityError:  # answered at the same moment from another device
        raise ValidationError('Câu này đã được trả lời rồi.')
    return answer


def streaks(couple, today=None):
    """(current, longest) runs of consecutive days on which either partner answered a question.
    The current streak stays alive through today if the last answer was yesterday."""
    today = today or timezone.localdate()
    days = sorted(set(Answer.objects.filter(question__couple=couple).values_list('answered_on', flat=True)))
    longest = run = 0
    previous = None
    for day in days:
        run = run + 1 if previous and day - previous == timedelta(days=1) else 1
        longest = max(longest, run)
        previous = day
    current = run if previous and today - previous <= timedelta(days=1) else 0
    return current, longest
