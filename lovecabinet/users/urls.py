from django.urls import path
from users import views

urlpatterns = [
    path('health',views.health,name='health'),
    path('users/<int:user_id>', views.get_user, name='users')
]