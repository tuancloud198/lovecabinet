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
    points_awarded = models.PositiveSmallIntegerField(default=0)  # points this memory earned (0 once the day's limit is reached)
class Comment(Timestamped):
    memory = models.ForeignKey(Memory, on_delete=models.CASCADE, related_name='comments')
    author = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    text = models.CharField(max_length=1000)
class Reaction(Timestamped):
    memory = models.ForeignKey(Memory, on_delete=models.CASCADE, related_name='reactions')
    author = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    class Meta:
        constraints = [models.UniqueConstraint(fields=['memory', 'author'], name='one_reaction_per_user')]


# Keep the couple's points in step with its memories (also when a jar or the couple is deleted with them).
# A memory earns MEMORY_POINTS within the daily limit; what it got is kept on it and taken back on delete.
from django.db.models.signals import post_save, pre_delete
from django.dispatch import receiver


def _couple_id(memory):
    return memory.jar.cabinet.couple_id


@receiver(post_save, sender=Memory)
def memory_saved(sender, instance, created, raw=False, **kwargs):
    from couples.models import MEMORY_POINTS
    from couples.points import award
    if created and not raw:
        instance.points_awarded = award(_couple_id(instance), MEMORY_POINTS)
        Memory.objects.filter(pk=instance.pk).update(points_awarded=instance.points_awarded)


@receiver(pre_delete, sender=Memory)
def memory_deleted(sender, instance, **kwargs):
    from django.utils import timezone
    from couples.points import take_back
    take_back(_couple_id(instance), instance.points_awarded, timezone.localdate(instance.created_at))
