"""
URL configuration for echo_occupancy project.
"""
from django.contrib import admin
from django.urls import path, include
from django.shortcuts import redirect

def home_view(request):
    """Home view that redirects based on authentication"""
    if request.user.is_authenticated:
        return redirect('rooms:dashboard')
    else:
        return redirect('accounts:login')

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', home_view, name='home'),
    path('', include('accounts.urls')),
    path('rooms/', include('rooms.urls')),
    path('reservations/', include('reservations.urls')),
]

