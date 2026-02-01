from django.db import models
from django.conf import settings


class Room(models.Model):
    """Room model representing the 40 rooms"""
    room_number = models.CharField(max_length=10, unique=True)
    has_iot_device = models.BooleanField(default=False, help_text='Whether this room has an IoT device connected')
    iot_device_id = models.CharField(max_length=100, blank=True, null=True, help_text='Firebase device ID')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['room_number']
        verbose_name = 'Room'
        verbose_name_plural = 'Rooms'
    
    def __str__(self):
        return f'Room {self.room_number}'
    
    def get_current_occupancy_status(self):
        """Get the latest occupancy status from Firebase or Reservation"""
        from reservations.models import Reservation
        from django.utils import timezone
        
        # Check if room is currently reserved/rented (exclude manager reservations)
        # Only consider it reserved if today is within the reservation period
        today = timezone.now().date()
        all_reservations = Reservation.objects.filter(
            room=self,
            status__in=['reserved', 'active']
        ).exclude(user__role='manager')
        
        active_reservation = None
        for res in all_reservations:
            if res.check_in and res.check_out:
                check_in_date = res.check_in.date() if hasattr(res.check_in, 'date') else res.check_in
                check_out_date = res.check_out.date() if hasattr(res.check_out, 'date') else res.check_out
                # Only consider it active if today is within the reservation period
                if check_in_date <= today <= check_out_date:
                    active_reservation = res
                    break
            elif not res.check_in and not res.check_out:
                # If no dates, consider it active
                active_reservation = res
                break
        
        if active_reservation:
            return {
                'is_occupied': True,
                'is_reserved': True,
                'user': active_reservation.user,
                'occupancy_data': None
            }
        
        # If room has IoT device, get real-time data from Firebase
        if self.has_iot_device and self.iot_device_id:
            from rooms.firebase_service import FirebaseService
            try:
                firebase_service = FirebaseService()
                # Use shorter timeout to prevent hanging (1 second)
                occupancy_data = firebase_service.get_room_occupancy(self.iot_device_id, timeout=1)
                if occupancy_data:
                    return {
                        'is_occupied': occupancy_data.get('is_occupied', False),
                        'is_reserved': False,
                        'user': None,
                        'occupancy_data': occupancy_data
                    }
            except Exception as e:
                # Silently fail - don't block the page if Firebase is unavailable
                pass
        
        return {
            'is_occupied': False,
            'is_reserved': False,
            'user': None,
            'occupancy_data': None
        }


class OccupancyData(models.Model):
    """Historical occupancy data from IoT devices"""
    room = models.ForeignKey(Room, on_delete=models.CASCADE, related_name='occupancy_history')
    is_occupied = models.BooleanField(default=False)
    timestamp = models.DateTimeField(auto_now_add=True)
    sensor_data = models.JSONField(default=dict, blank=True, help_text='Raw sensor data from IoT device')
    
    class Meta:
        ordering = ['-timestamp']
        verbose_name = 'Occupancy Data'
        verbose_name_plural = 'Occupancy Data'
    
    def __str__(self):
        return f'{self.room.room_number} - {self.timestamp}'

