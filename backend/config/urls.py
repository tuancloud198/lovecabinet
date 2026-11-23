from django.urls import path, include
from rest_framework.routers import DefaultRouter
from users import views as users
from couple_invitations import views as invitations
from couples.views import CoupleViewSet
from cabinets.views import CabinetViewSet
from jars.views import JarViewSet
from memories.views import MemoryViewSet
from photos.views import PhotoViewSet, stream as photo_stream
from events.views import EventViewSet
from common import health
router = DefaultRouter()
for prefix, view, basename in [('couples', CoupleViewSet, 'couple'), ('cabinets', CabinetViewSet, 'cabinet'), ('jars', JarViewSet, 'jar'), ('memories', MemoryViewSet, 'memory'), ('photos', PhotoViewSet, 'photo'), ('events', EventViewSet, 'event')]:
    router.register(prefix, view, basename=basename)
urlpatterns = [path('api/photos/<int:pk>/stream/', photo_stream), path('api/healthz/', health.live), path('api/readyz/', health.ready), path('api/auth/register/', users.register), 
                path('api/auth/login/', users.login), 
                path('api/auth/logout/', users.logout), 
                path('api/auth/google/', users.google), 
                path('api/auth/config/', users.auth_config), 
                path('api/users/me/', users.me), 
                path('api/couple-invitations/', 
                invitations.invitations), 
                path('api/couple-invitations/<int:pk>/accept/', invitations.accept), 
                path('api/couple-invitations/<int:pk>/decline/', invitations.decline), 
                path('api/', include(router.urls))]
