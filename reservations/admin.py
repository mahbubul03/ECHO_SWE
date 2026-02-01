from django.contrib import admin
from .models import Reservation


@admin.register(Reservation)
class ReservationAdmin(admin.ModelAdmin):
    list_display = ['user', 'room', 'status', 'reserved_at', 'check_in', 'check_out']
    list_filter = ['status', 'reserved_at']
    search_fields = ['user__username', 'room__room_number']
    readonly_fields = ['reserved_at']
    date_hierarchy = 'reserved_at'

