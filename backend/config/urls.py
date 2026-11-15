from django.urls import path, include
from rest_framework.routers import DefaultRouter
from users import views as users
from couple_invitations import views as invitations
from couples.views import CoupleViewSet
from cabinets.views import CabinetViewSet
from jars.views import JarViewSet
from memories.views import MemoryViewSet
from photos.views import PhotoViewSet
from events.views import EventViewSet
router = DefaultRouter()
for prefix, view, basename in [('couples', CoupleViewSet, 'couple'), ('cabinets', CabinetViewSet, 'cabinet'), ('jars', JarViewSet, 'jar'), ('memories', MemoryViewSet, 'memory'), ('photos', PhotoViewSet, 'photo'), ('events', EventViewSet, 'event')]:
    router.register(prefix, view, basename=basename)
urlpatterns = [path('api/auth/register/', users.register), path('api/auth/login/', users.login), path('api/auth/logout/', users.logout), path('api/users/me/', users.me), path('api/couple-invitations/', invitations.create), path('api/couple-invitations/accept/', invitations.accept), path('api/', include(router.urls))]
