from django.contrib.auth.models import AbstractUser
from django.db import models

class User(AbstractUser):
    """Custom user model for BIMS"""
    
    ROLE_CHOICES = [
        ('admin', 'Administrator'),
        ('clerk', 'Clerk'),
        ('treasurer', 'Treasurer'),
    ]
    
    role = models.CharField(max_length=20, choices=ROLE_CHOICES, default='clerk')
    barangay_position = models.CharField(max_length=100, blank=True, null=True, help_text="Official designation (e.g., Barangay Secretary)")
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        verbose_name = 'User'
        verbose_name_plural = 'Users'

    groups = models.ManyToManyField(
        'auth.Group',
        related_name='custom_user_set',
        blank=True,
        help_text='The groups this user belongs to.',
        verbose_name='groups',
    )
    user_permissions = models.ManyToManyField(
        'auth.Permission',
        related_name='custom_user_set',
        blank=True,
        help_text='Specific permissions for this user.',
        verbose_name='user permissions',
    )
        
    def __str__(self):
        return f"{self.username} - {self.get_role_display()}"
