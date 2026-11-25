from django.db import models
from django.conf import settings
from common.models import Timestamped
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
    pet_points = models.PositiveIntegerField(default=0)  # earned outside memories (quiz answers); memories count on top
class Membership(models.Model):
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='membership')
    couple = models.ForeignKey(Couple, on_delete=models.CASCADE, related_name='memberships')
