from django.urls import path
from . import views

app_name = 'reservations'

urlpatterns = [
    path('', views.reservation_page, name='reservation_page'),
    path('reserve/<str:room_number>/', views.reserve_room, name='reserve_room'),
    path('cancel/<int:reservation_id>/', views.cancel_reservation, name='cancel_reservation'),
]

