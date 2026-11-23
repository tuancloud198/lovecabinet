from rest_framework import mixins, viewsets
from couples.serializers.couple_serializers import CoupleSerializer
from couples.services import for_user, update_couple
class CoupleViewSet(mixins.UpdateModelMixin, viewsets.ReadOnlyModelViewSet):
    """Members can read their couple and update its name, our dates (met / dating since) and pet."""
    serializer_class = CoupleSerializer
    def get_queryset(self):
        return for_user(self.request.user)
    def perform_update(self, serializer):
        update_couple(serializer)
