from django.db import IntegrityError, transaction
from rest_framework.exceptions import ValidationError
from cabinets.models import Cabinet
from common.services import couple_for, save_scoped

def save(serializer, user, scope):
    """A couple has one cabinet per year: creating a year that already exists returns that cabinet.

    The partner's app may not have seen a cabinet the other one just created, so asking for it
    again is normal and must not make a second cabinet."""
    couple = couple_for(user)
    year = serializer.validated_data.get('year', getattr(serializer.instance, 'year', Cabinet._meta.get_field('year').default))
    existing = Cabinet.objects.filter(couple=couple, year=year).exclude(pk=getattr(serializer.instance, 'pk', None)).first()
    if existing:
        if serializer.instance is not None:
            raise ValidationError('Tủ của năm này đã tồn tại.')
        serializer.instance = existing
        return existing
    try:
        with transaction.atomic():
            return save_scoped(serializer, user, scope)
    except IntegrityError:
        # Both partners created the same year at the same moment: use the one that won.
        existing = Cabinet.objects.filter(couple=couple, year=year).first()
        if not existing or serializer.instance is not None:
            raise
        serializer.instance = existing
        return existing
