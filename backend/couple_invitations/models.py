import secrets
from datetime import timedelta
from django.db import models
from django.conf import settings
from django.utils import timezone
from common.models import Timestamped
def code():
    # No longer used by the model; referenced by migration 0001_initial.
    return secrets.token_hex(5).upper()
def expiry():
    return timezone.now() + timedelta(days=2)
class Invitation(Timestamped):
    sender = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='sent_invitations')
    recipient = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='received_invitations')
    expires_at = models.DateTimeField(default=expiry)
    accepted_at = models.DateTimeField(null=True, blank=True)
    declined_at = models.DateTimeField(null=True, blank=True)
