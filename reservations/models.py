from django.db import models
from django.conf import settings
from rooms.models import Room


class Reservation(models.Model):
    """Reservation model linking users to rooms"""
    STATUS_CHOICES = [
        ('reserved', 'Reserved'),
        ('active', 'Active'),
        ('completed', 'Completed'),
        ('cancelled', 'Cancelled'),
    ]
    
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='reservations'
    )
    room = models.ForeignKey(
        Room,
        on_delete=models.CASCADE,
        related_name='reservations'
    )
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='reserved'
    )
    reserved_at = models.DateTimeField(auto_now_add=True)
    check_in = models.DateTimeField(blank=True, null=True)
    check_out = models.DateTimeField(blank=True, null=True)
    notes = models.TextField(blank=True)
    
    class Meta:
        ordering = ['-reserved_at']
        verbose_name = 'Reservation'
        verbose_name_plural = 'Reservations'
        # Note: Unique constraint for active reservations is enforced in views
    
    def __str__(self):
        return f'{self.user.username} - Room {self.room.room_number} ({self.status})'

