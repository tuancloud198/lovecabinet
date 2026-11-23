from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models
from django.conf import settings
from common.models import Timestamped
class Memory(Timestamped):
    jar = models.ForeignKey('jars.Jar', on_delete=models.CASCADE, related_name='memories')
    author = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    title = models.CharField(max_length=150)
    story = models.TextField(blank=True, max_length=5000)
    date = models.DateField()
    emoji = models.CharField(max_length=16, default='❤️')
    # Where it happened (one pin per memory on the map): from the photos' GPS, the phone's location or picked by hand.
    latitude = models.FloatField(null=True, blank=True, validators=[MinValueValidator(-90), MaxValueValidator(90)])
    longitude = models.FloatField(null=True, blank=True, validators=[MinValueValidator(-180), MaxValueValidator(180)])
    place = models.CharField(max_length=120, blank=True)
class Comment(Timestamped):
    memory = models.ForeignKey(Memory, on_delete=models.CASCADE, related_name='comments')
    author = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    text = models.CharField(max_length=1000)
class Reaction(Timestamped):
    memory = models.ForeignKey(Memory, on_delete=models.CASCADE, related_name='reactions')
    author = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    class Meta:
        constraints = [models.UniqueConstraint(fields=['memory', 'author'], name='one_reaction_per_user')]
