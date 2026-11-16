from django.db import transaction
from django.utils import timezone
from rest_framework.exceptions import NotFound, ValidationError
from users.models import User, normalize_tag
from couples.models import Couple, Membership
from cabinets.models import Cabinet
from couple_invitations.models import Invitation

def pending_invitations():
    return Invitation.objects.filter(accepted_at__isnull=True, declined_at__isnull=True, expires_at__gt=timezone.now()).select_related('sender', 'recipient')

def list_invitations(user):
    pending = pending_invitations()
    return pending.filter(recipient=user), pending.filter(sender=user)

def create_invitation(user, tag):
    recipient = User.objects.filter(tag=normalize_tag(tag)).first()
    if not recipient:
        raise ValidationError('Không tìm thấy người dùng với mã này.')
    if recipient.pk == user.pk:
        raise ValidationError('Bạn không thể ghép đôi với chính mình.')
    if Membership.objects.filter(user_id__in=[user.pk, recipient.pk]).exists():
        raise ValidationError('Một trong hai người đã ghép đôi.')
    existing = pending_invitations().filter(sender=user, recipient=recipient).first()
    return existing or Invitation.objects.create(sender=user, recipient=recipient)

def locked_pending_invitation(user, invitation_id):
    invitation = Invitation.objects.select_for_update().filter(pk=invitation_id, recipient=user).first()
    if not invitation:
        raise NotFound('Không tìm thấy lời mời.')
    if invitation.accepted_at or invitation.declined_at or invitation.expires_at <= timezone.now():
        raise ValidationError('Lời mời không hợp lệ hoặc đã hết hạn.')
    return invitation

def decline_invitation(user, invitation_id):
    with transaction.atomic():
        invitation = locked_pending_invitation(user, invitation_id)
        invitation.declined_at = timezone.now()
        invitation.save(update_fields=['declined_at'])

def accept_invitation(user, invitation_id):
    with transaction.atomic():
        invitation = locked_pending_invitation(user, invitation_id)
        list(User.objects.select_for_update().filter(pk__in=[user.pk, invitation.sender_id]).order_by('pk'))
        if Membership.objects.filter(user_id__in=[user.pk, invitation.sender_id]).exists():
            raise ValidationError('Một trong hai người đã ghép đôi.')
        couple = Couple.objects.create()
        Membership.objects.bulk_create([Membership(user_id=uid, couple=couple) for uid in [user.pk, invitation.sender_id]])
        Cabinet.objects.create(couple=couple, name='Tủ thương', year=timezone.localdate().year)
        invitation.accepted_at = timezone.now()
        invitation.save()
    return couple
