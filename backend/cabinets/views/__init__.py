from common.api import ScopedViewSet
from cabinets.models import Cabinet
from cabinets.serializers.cabinet_serializers import CabinetSerializer
class CabinetViewSet(ScopedViewSet):
    queryset = Cabinet.objects.all()
    serializer_class = CabinetSerializer
    scope = 'couple'

    def perform_create(self, serializer):
        from cabinets.services import save
        save(serializer, self.request.user, self.scope)
    def perform_update(self, serializer):
        self.perform_create(serializer)
