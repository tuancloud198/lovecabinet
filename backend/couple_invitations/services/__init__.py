from django.db import transaction
from django.utils import timezone
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework.exceptions import ValidationError
from users.models import User
from couples.models import Couple, Membership
from cabinets.models import Cabinet
from ..models import Invitation
def create_invitation(user):
    if Membership.objects.filter(user=user).exists():
        raise ValidationError('Bạn đã ghép đôi.')
    invitation = Invitation.objects.create(sender=user)
    return invitation
def accept_invitation(user, code):
    with transaction.atomic():
        invitation = Invitation.objects.select_for_update().filter(code=str(code).upper()).first()
        if not invitation or invitation.accepted_at or invitation.expires_at <= timezone.now():
            raise ValidationError('Mã không hợp lệ hoặc đã hết hạn.')
        if invitation.sender_id == user.pk:
            raise ValidationError('Bạn không thể ghép đôi với chính mình.')
        list(User.objects.select_for_update().filter(pk__in=[user.pk, invitation.sender_id]).order_by('pk'))
        if Membership.objects.filter(user_id__in=[user.pk, invitation.sender_id]).exists():
            raise ValidationError('Một trong hai người đã ghép đôi.')
        couple = Couple.objects.create()
        Membership.objects.bulk_create([Membership(user_id=uid, couple=couple) for uid in [user.pk, invitation.sender_id]])
        Cabinet.objects.create(couple=couple, name='Tủ thương', year=timezone.localdate().year)
        invitation.accepted_by = user
        invitation.accepted_at = timezone.now()
        invitation.save()
    return couple
