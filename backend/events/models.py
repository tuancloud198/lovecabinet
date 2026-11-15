from django.db import models
from common.models import Timestamped
class Event(Timestamped):
    couple = models.ForeignKey('couples.Couple', on_delete=models.CASCADE, related_name='events')
    title = models.CharField(max_length=150)
    date = models.DateField()
    emoji = models.CharField(max_length=16, default='🎂')
