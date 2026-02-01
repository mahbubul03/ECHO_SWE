from django.urls import path
from . import views

app_name = 'rooms'

urlpatterns = [
    path('', views.dashboard, name='dashboard'),
    path('<str:room_number>/', views.room_detail, name='room_detail'),
]

