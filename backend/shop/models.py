from django.conf import settings
from django.db import models
from common.models import Timestamped

# What the shop sells. Prices are in pet points; buying spends shop points only (pet growth keeps
# every point earned). Add new items here .
ITEMS = {
    'theme_pink': {'kind': 'theme', 'name': 'Hồng ngọt ngào', 'description': 'Giao diện hồng phấn dịu dàng cho cả app.', 'price': 50},
    'pet_cat': {'kind': 'pet', 'name': 'Mèo Mướp', 'description': 'Chú mèo tinh nghịch, cả hai cùng nuôi nhé.', 'price': 50},
    'pet_ragdog': {'kind': 'pet', 'name': 'Cún Khố Rách', 'description': 'Khố rách áo ôm nhưng thương hai bạn hết lòng.', 'price': 300},
}


class Purchase(Timestamped):
    """An item the couple bought (shared by both partners; bought once)."""
    couple = models.ForeignKey('couples.Couple', on_delete=models.CASCADE, related_name='purchases')
    buyer = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, related_name='purchases')
    item = models.CharField(max_length=40)
    price = models.PositiveIntegerField()

    class Meta:
        constraints = [models.UniqueConstraint(fields=['couple', 'item'], name='buy_each_item_once')]
