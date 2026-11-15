from rest_framework import viewsets
from ..serializers import CoupleSerializer
from ..services import for_user
class CoupleViewSet(viewsets.ReadOnlyModelViewSet):
    serializer_class = CoupleSerializer
    def get_queryset(self):
        return for_user(self.request.user)
