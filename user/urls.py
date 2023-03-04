from django.urls import path
from .views import register, verification, login_view, logout_view

urlpatterns = [
    path('register/', register, name='register'),
    path('verification/', verification, name='verification'),
    path('login/', login_view, name='login'),
    path('logout/', logout_view, name='logout'),
]