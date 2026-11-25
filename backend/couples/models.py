from django.db import models
from django.conf import settings
from common.models import Timestamped
# Points: each memory and each answered quiz question earns the couple points (they grow the pet); the shop
# spends them. Stored on the couple and kept up to date as things happen (memories/models.py, quizzes, shop).
MEMORY_POINTS = 10
QUIZ_POINTS = 2
# At most this many points a day (memories + answers together, reset at local midnight): stops farming points
# by adding throwaway memories to buy things. Points earned before the limit existed are kept as they were.
DAILY_POINTS_LIMIT = 100
PET_MOODS = [('', 'Tự động'), ('neutral', 'Bình thản'), ('happy', 'Vui vẻ'), ('shy', 'Ngại ngùng'), ('excited', 'Phấn khích')]
PET_TYPES = [('dog', 'Cún'), ('cat', 'Mèo'), ('capybara', 'Capybara'), ('honey_badger', 'Lửng mật'), ('hamster', 'Hamster'), ('ragdog', 'Cún Khố Rách')]
class Couple(Timestamped):
    name = models.CharField(max_length=100, default='Tủ thương của chúng ta')
    # Our story: the day we first met and the day we started loving each other (day 1 of the day count).
    met_on = models.DateField(null=True, blank=True)
    dating_since = models.DateField(null=True, blank=True)
    pet_name = models.CharField(max_length=50, default='Bờm')
    pet_type = models.CharField(max_length=20, choices=PET_TYPES, default='dog')
    # The face on the big pet picture, picked by the couple; '' = the automatic mood (from the latest memory).
    pet_mood = models.CharField(max_length=10, choices=PET_MOODS, blank=True, default='')
    points_earned = models.IntegerField(default=0)  # memories x MEMORY_POINTS + answers x QUIZ_POINTS (a deleted memory takes its points back)
    points_spent = models.PositiveIntegerField(default=0)  # sum of shop purchases; spending never shrinks the pet

    @property
    def points_balance(self):
        return max(0, self.points_earned - self.points_spent)

class DailyPoints(models.Model):
    """Points a couple earned on one day, against that day's limit (e.g. 2026-11-25 · limit 100 · earned 85).
    A row is made the first time either partner earns points that day (a memory, a quiz answer)."""
    couple = models.ForeignKey(Couple, on_delete=models.CASCADE, related_name='daily_points')
    day = models.DateField()
    limit = models.PositiveIntegerField(default=DAILY_POINTS_LIMIT)
    earned = models.PositiveIntegerField(default=0)

    class Meta:
        ordering = ['-day']
        constraints = [models.UniqueConstraint(fields=['couple', 'day'], name='one_points_row_per_couple_day')]


class Membership(models.Model):
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='membership')
    couple = models.ForeignKey(Couple, on_delete=models.CASCADE, related_name='memberships')
