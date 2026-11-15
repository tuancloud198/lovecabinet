from rest_framework.exceptions import ValidationError

def couple_for(user):
    from couples.models import Membership
    membership = Membership.objects.filter(user=user).first()
    if not membership:
        raise ValidationError('Bạn cần ghép đôi trước.')
    return membership.couple

def save_scoped(serializer, user, scope):
    couple = couple_for(user)
    field = scope.split('__')[0]
    if field == 'couple':
        return serializer.save(couple=couple)
    current = serializer.validated_data.get(field, getattr(serializer.instance, field, None))
    for part in scope.split('__')[1:]:
        current = getattr(current, part)
    if current.pk != couple.pk:
        raise ValidationError('Không có quyền truy cập.')
    extra = {'author': user} if 'author' in [f.name for f in serializer.Meta.model._meta.fields] and serializer.instance is None else {}
    return serializer.save(**extra)
