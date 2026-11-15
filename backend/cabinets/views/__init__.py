from common.api import ScopedViewSet
from ..models import Cabinet
from ..serializers import CabinetSerializer
class CabinetViewSet(ScopedViewSet):
    queryset = Cabinet.objects.all()
    serializer_class = CabinetSerializer
    scope = 'couple'

    def perform_create(self, serializer):
        from ..services import save
        save(serializer, self.request.user, self.scope)
    def perform_update(self, serializer):
        self.perform_create(serializer)
