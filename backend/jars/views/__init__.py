from common.api import ScopedViewSet
from jars.models import Jar
from jars.serializers.jar_serializers import JarSerializer
class JarViewSet(ScopedViewSet):
    queryset = Jar.objects.all()
    serializer_class = JarSerializer
    scope = 'cabinet__couple'

    def perform_create(self, serializer):
        from jars.services import save
        save(serializer, self.request.user, self.scope)
    def perform_update(self, serializer):
        self.perform_create(serializer)
