from django.db import models
from common.models import Timestamped
class Jar(Timestamped):
    cabinet = models.ForeignKey('cabinets.Cabinet', on_delete=models.CASCADE, related_name='jars')
    name = models.CharField(max_length=100)
    emoji = models.CharField(max_length=16, default='❤️')
    color = models.CharField(max_length=7, default='#FBE5DD')
