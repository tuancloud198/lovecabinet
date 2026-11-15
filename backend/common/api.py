from rest_framework import viewsets
from .services import couple_for, save_scoped
class ScopedViewSet(viewsets.ModelViewSet):
    scope = 'couple'
    def get_queryset(self):
        return self.queryset.filter(**{self.scope: couple_for(self.request.user)})
    def perform_create(self, serializer):
        save_scoped(serializer, self.request.user, self.scope)
    def perform_update(self, serializer):
        save_scoped(serializer, self.request.user, self.scope)
    def perform_destroy(self, instance):
        from .deletion import delete_with_photos
        scopes = {'Cabinet': 'memory__jar__cabinet', 'Jar': 'memory__jar', 'Memory': 'memory'}
        scope = scopes.get(type(instance).__name__)
        if scope:
            delete_with_photos(instance, scope)
        else:
            instance.delete()
