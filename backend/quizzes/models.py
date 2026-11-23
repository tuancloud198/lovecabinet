from django.conf import settings
from django.db import models
from common.models import Timestamped


class Question(Timestamped):
    """A multiple-choice question one partner writes (about themselves) for the other to answer."""
    couple = models.ForeignKey('couples.Couple', on_delete=models.CASCADE, related_name='quiz_questions')
    author = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='quiz_questions')
    text = models.CharField(max_length=200)
    choices = models.JSONField()  # 2-4 strings
    correct = models.PositiveSmallIntegerField()  # index into choices


class Answer(Timestamped):
    """The partner's answer (one per question). `answered_on` (local date) drives the daily streak."""
    question = models.OneToOneField(Question, on_delete=models.CASCADE, related_name='answer')
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='quiz_answers')
    choice = models.PositiveSmallIntegerField()
    answered_on = models.DateField()

    @property
    def is_correct(self):
        return self.choice == self.question.correct
