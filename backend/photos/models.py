from django.db import models
from common.models import Timestamped
class Photo(Timestamped):
    memory = models.ForeignKey('memories.Memory', on_delete=models.CASCADE, related_name='photos')
    object_key = models.CharField(max_length=500, unique=True)
    content_type = models.CharField(max_length=100)
