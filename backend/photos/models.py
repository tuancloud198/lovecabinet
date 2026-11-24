from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models
from common.models import Timestamped
class Photo(Timestamped):
    memory = models.ForeignKey('memories.Memory', on_delete=models.CASCADE, related_name='photos')
    object_key = models.CharField(max_length=500, unique=True)
    content_type = models.CharField(max_length=100)
    # Where this photo/video was taken (its own GPS). A memory can span several places; items without
    # their own location count as being at the memory's location.
    latitude = models.FloatField(null=True, blank=True, validators=[MinValueValidator(-90), MaxValueValidator(90)])
    longitude = models.FloatField(null=True, blank=True, validators=[MinValueValidator(-180), MaxValueValidator(180)])
    place = models.CharField(max_length=120, blank=True)
    # Smaller JPEG copies next to the original ({name}.thumb.jpg, {name}.display.jpg); photos only.
    variants = models.BooleanField(default=False)
