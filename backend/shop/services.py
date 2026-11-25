from django.db import IntegrityError, models, transaction
from rest_framework.exceptions import NotFound, ValidationError
from couples.models import Couple
from shop.models import Purchase, ShopItem

def wallet(couple):
    """Points earned (the pet's total), spent in the shop, and what's left to spend (stored on the couple)."""
    return {'earned': couple.points_earned, 'spent': couple.points_spent, 'balance': couple.points_balance}


def catalog(couple):
    """Items on sale, plus any the couple bought that aren't sold any more."""
    owned = set(Purchase.objects.filter(couple=couple).values_list('item', flat=True))
    items = ShopItem.objects.filter(models.Q(active=True) | models.Q(key__in=owned))
    return [{'id': i.key, 'kind': i.kind, 'name': i.name, 'description': i.description, 'price': i.price, 'owned': i.key in owned} for i in items]


def buy(couple, user, item_id):
    item = ShopItem.objects.filter(key=item_id, active=True).first()
    if not item:
        raise NotFound('Không có món này trong cửa hàng.')
    with transaction.atomic():
        locked = Couple.objects.select_for_update().get(pk=couple.pk)  # one purchase at a time per couple
        if Purchase.objects.filter(couple=couple, item=item_id).exists():
            raise ValidationError('Hai bạn đã có món này rồi.')
        if locked.points_balance < item.price:
            raise ValidationError('Chưa đủ điểm để mua món này.')
        try:
            with transaction.atomic():
                Purchase.objects.create(couple=couple, buyer=user, item=item, price=item.price)
        except IntegrityError:
            raise ValidationError('Hai bạn đã có món này rồi.')
        locked.points_spent += item.price
        locked.save(update_fields=['points_spent'])
    couple.refresh_from_db(fields=['points_earned', 'points_spent'])


def owned_themes(user):
    from common.services import couple_for
    keys = Purchase.objects.filter(couple=couple_for(user), item__kind='theme').values_list('item', flat=True)
    return {key.removeprefix('theme_') for key in keys}
