from couples.models import Couple

def update_couple(serializer):
    return serializer.save()

def for_user(user):
    return Couple.objects.filter(memberships__user=user)
