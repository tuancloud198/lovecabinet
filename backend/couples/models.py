from django.db import models
from django.conf import settings
from common.models import Timestamped
class Couple(Timestamped):
    name = models.CharField(max_length=100, default='Tủ thương của chúng ta')
    anniversary = models.DateField(null=True, blank=True)
    pet_name = models.CharField(max_length=50, default='Bờm')
class Membership(models.Model):
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='membership')
    couple = models.ForeignKey(Couple, on_delete=models.CASCADE, related_name='memberships')
