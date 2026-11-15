from common.api import ScopedViewSet
from ..models import Event
from ..serializers import EventSerializer
class EventViewSet(ScopedViewSet):
    queryset = Event.objects.all()
    serializer_class = EventSerializer
    scope = 'couple'

    def perform_create(self, serializer):
        from ..services import save
        save(serializer, self.request.user, self.scope)
    def perform_update(self, serializer):
        self.perform_create(serializer)
