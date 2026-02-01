from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):
    """Custom User model with role field"""
    ROLE_CHOICES = [
        ('manager', 'Manager'),
        ('normal', 'Normal User'),
    ]
    
    role = models.CharField(
        max_length=10,
        choices=ROLE_CHOICES,
        default='normal',
        help_text='User role: Manager can see all rooms, Normal User can only see their room'
    )
    
    def is_manager(self):
        return self.role == 'manager'
    
    def is_normal_user(self):
        return self.role == 'normal'
    
    class Meta:
        verbose_name = 'User'
        verbose_name_plural = 'Users'

