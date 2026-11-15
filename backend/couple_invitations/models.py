import secrets
from datetime import timedelta
from django.db import models
from django.conf import settings
from django.utils import timezone
from common.models import Timestamped
def code():
    return secrets.token_hex(5).upper()
def expiry():
    return timezone.now() + timedelta(days=2)
class Invitation(Timestamped):
    sender = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    code = models.CharField(max_length=10, unique=True, default=code)
    expires_at = models.DateTimeField(default=expiry)
    accepted_by = models.ForeignKey(settings.AUTH_USER_MODEL, null=True, blank=True, on_delete=models.SET_NULL, related_name='accepted_invitations')
    accepted_at = models.DateTimeField(null=True, blank=True)
