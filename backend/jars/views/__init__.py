from common.api import ScopedViewSet
from ..models import Jar
from ..serializers import JarSerializer
class JarViewSet(ScopedViewSet):
    queryset = Jar.objects.all()
    serializer_class = JarSerializer
    scope = 'cabinet__couple'

    def perform_create(self, serializer):
        from ..services import save
        save(serializer, self.request.user, self.scope)
    def perform_update(self, serializer):
        self.perform_create(serializer)
