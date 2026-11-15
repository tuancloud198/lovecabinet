from ..models import Couple

def for_user(user):
    return Couple.objects.filter(memberships__user=user)
