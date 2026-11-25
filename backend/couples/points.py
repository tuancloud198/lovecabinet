"""Earning points (memories, quiz answers) within the couple's daily limit, tracked in DailyPoints."""
from django.db import transaction
from django.utils import timezone
from couples.models import Couple, DailyPoints


def today_points(couple, today=None):
    """(earned today, today's limit). No row yet = nothing earned today, the current limit."""
    row = DailyPoints.objects.filter(couple=couple, day=today or timezone.localdate()).first()
    return (row.earned, row.limit) if row else (0, DailyPoints._meta.get_field('limit').default)


def award(couple_id, points):
    """Give the couple up to `points`, as much as today's limit still allows. Returns what was given."""
    today = timezone.localdate()
    with transaction.atomic():
        couple = Couple.objects.select_for_update().filter(pk=couple_id).first()  # one award at a time per couple
        if not couple:
            return 0
        row, _ = DailyPoints.objects.get_or_create(couple=couple, day=today)
        given = max(0, min(points, row.limit - row.earned))
        if given:
            row.earned += given
            row.save(update_fields=['earned'])
            couple.points_earned += given
            couple.save(update_fields=['points_earned'])
    return given


def take_back(couple_id, points, earned_on):
    """Remove points a deleted memory earned on `earned_on`, from the total and from that day's row (deleting a
    memory made today gives today's allowance back, so deleting and adding it again is even)."""
    if not points:
        return
    with transaction.atomic():
        couple = Couple.objects.select_for_update().filter(pk=couple_id).first()
        if not couple:
            return
        couple.points_earned -= points
        couple.save(update_fields=['points_earned'])
        row = DailyPoints.objects.filter(couple=couple, day=earned_on).first()
        if row:
            row.earned = max(0, row.earned - points)
            row.save(update_fields=['earned'])
