from django.contrib import admin
from .models import Room, OccupancyData


@admin.register(Room)
class RoomAdmin(admin.ModelAdmin):
    list_display = ['room_number', 'has_iot_device', 'iot_device_id']
    list_filter = ['has_iot_device']
    search_fields = ['room_number']


@admin.register(OccupancyData)
class OccupancyDataAdmin(admin.ModelAdmin):
    list_display = ['room', 'is_occupied', 'timestamp']
    list_filter = ['is_occupied', 'timestamp']
    readonly_fields = ['timestamp']
    date_hierarchy = 'timestamp'

