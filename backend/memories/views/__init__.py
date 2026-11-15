from rest_framework.decorators import action
from rest_framework.response import Response
from common.api import ScopedViewSet
from ..models import Memory
from ..serializers import MemorySerializer, CommentSerializer
from ..services import save_memory, add_comment, toggle_reaction
class MemoryViewSet(ScopedViewSet):
    queryset = Memory.objects.select_related('author').prefetch_related('photos', 'comments__author', 'reactions')
    serializer_class = MemorySerializer
    scope = 'jar__cabinet__couple'
    @action(detail=True, methods=['post'])
    def comment(self, request, pk=None):
        memory = self.get_object()
        s = CommentSerializer(data=request.data)
        s.is_valid(raise_exception=True)
        add_comment(s, memory, request.user)
        return Response(s.data, status=201)
    @action(detail=True, methods=['post'])
    def react(self, request, pk=None):
        memory = self.get_object()
        return Response({'liked': toggle_reaction(memory, request.user)})
    def perform_create(self, serializer):
        save_memory(serializer, self.request.user)
    def perform_update(self, serializer):
        self.perform_create(serializer)
