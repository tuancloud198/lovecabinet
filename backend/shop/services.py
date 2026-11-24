from django.db import IntegrityError, transaction
from django.db.models import Sum
from rest_framework.exceptions import NotFound, ValidationError
from couples.models import Couple
from shop.models import ITEMS, Purchase

MEMORY_POINTS = 10  # same as the pet (frontend characters.js): memory 10, quiz answer 2 (couple.pet_points)


def wallet(couple):
    """Points earned (the pet's total), spent in the shop, and what's left to spend."""
    from memories.models import Memory
    earned = Memory.objects.filter(jar__cabinet__couple=couple).count() * MEMORY_POINTS + couple.pet_points
    spent = Purchase.objects.filter(couple=couple).aggregate(total=Sum('price'))['total'] or 0
    return {'earned': earned, 'spent': spent, 'balance': max(0, earned - spent)}


def catalog(couple):
    owned = set(Purchase.objects.filter(couple=couple).values_list('item', flat=True))
    return [{'id': key, **item, 'owned': key in owned} for key, item in ITEMS.items()]


def buy(couple, user, item_id):
    item = ITEMS.get(item_id)
    if not item:
        raise NotFound('Không có món này trong cửa hàng.')
    with transaction.atomic():
        Couple.objects.select_for_update().get(pk=couple.pk)  # one purchase at a time per couple
        if Purchase.objects.filter(couple=couple, item=item_id).exists():
            raise ValidationError('Hai bạn đã có món này rồi.')
        if wallet(couple)['balance'] < item['price']:
            raise ValidationError('Chưa đủ điểm để mua món này.')
        try:
            Purchase.objects.create(couple=couple, buyer=user, item=item_id, price=item['price'])
        except IntegrityError:
            raise ValidationError('Hai bạn đã có món này rồi.')


def owned_themes(user):
    from common.services import couple_for
    keys = Purchase.objects.filter(couple=couple_for(user)).values_list('item', flat=True)
    return {key.removeprefix('theme_') for key in keys if ITEMS.get(key, {}).get('kind') == 'theme'}
