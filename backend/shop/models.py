from django.conf import settings
from django.db import models
from common.models import Timestamped

class ShopItem(Timestamped):
    """Something the shop sells. Prices are in pet points; buying spends shop points only (pet growth keeps
    every point earned). `key` is what the app uses: 'theme_<name>' (a look) or 'pet_<Couple.pet_type>'.
    Inactive items aren't sold any more, but couples who bought one keep it."""
    KINDS = [('theme', 'Giao diện'), ('pet', 'Bạn nhỏ')]
    key = models.CharField(max_length=40, primary_key=True)
    kind = models.CharField(max_length=10, choices=KINDS)
    name = models.CharField(max_length=60)
    description = models.CharField(max_length=200, blank=True)
    price = models.PositiveIntegerField()
    active = models.BooleanField(default=True)
    position = models.PositiveIntegerField(default=0)  # order in the shop

    class Meta:
        ordering = ['position', 'key']

    def __str__(self):
        return self.key


class Purchase(Timestamped):
    """An item the couple bought (shared by both partners; bought once)."""
    couple = models.ForeignKey('couples.Couple', on_delete=models.CASCADE, related_name='purchases')
    buyer = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, related_name='purchases')
    # Still the 'item' column (the item's key), now checked against the shop's items.
    item = models.ForeignKey(ShopItem, on_delete=models.PROTECT, db_column='item', related_name='purchases')
    price = models.PositiveIntegerField()  # what was paid (prices can change later)

    class Meta:
        constraints = [models.UniqueConstraint(fields=['couple', 'item'], name='buy_each_item_once')]
