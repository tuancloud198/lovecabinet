from django.db import models
from common.models import Timestamped
class Cabinet(Timestamped):
    couple = models.ForeignKey('couples.Couple', on_delete=models.CASCADE, related_name='cabinets')
    name = models.CharField(max_length=100)
    year = models.PositiveIntegerField(default=2026)
    class Meta(Timestamped.Meta):
        constraints = [models.UniqueConstraint(fields=['couple', 'year'], name='one_cabinet_per_couple_year')]
