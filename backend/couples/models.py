from django.db import models
from django.conf import settings
from common.models import Timestamped
PET_TYPES = [('dog', 'Cún'), ('cat', 'Mèo'), ('capybara', 'Capybara'), ('honey_badger', 'Lửng mật'), ('hamster', 'Hamster')]
class Couple(Timestamped):
    name = models.CharField(max_length=100, default='Tủ thương của chúng ta')
    # Our story: the day we first met and the day we started loving each other (day 1 of the day count).
    met_on = models.DateField(null=True, blank=True)
    dating_since = models.DateField(null=True, blank=True)
    pet_name = models.CharField(max_length=50, default='Bờm')
    pet_type = models.CharField(max_length=20, choices=PET_TYPES, default='dog')
class Membership(models.Model):
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='membership')
    couple = models.ForeignKey(Couple, on_delete=models.CASCADE, related_name='memberships')
