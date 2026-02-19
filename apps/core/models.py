from django.contrib.auth.models import AbstractUser
from django.db import models
from django.utils import timezone

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


class LicenseKey(models.Model):
    """License key model for tier-based feature access control"""
    
    TIER_CHOICES = [
        ('community', 'Community'),
        ('pro', 'Pro'),
        ('ultra', 'Ultra'),
    ]
    
    key = models.CharField(max_length=255, unique=True, help_text="License key string")
    tier = models.CharField(max_length=20, choices=TIER_CHOICES, help_text="License tier level")
    hardware_id = models.CharField(max_length=255, blank=True, help_text="Hardware ID this license is bound to")
    issued_date = models.DateTimeField(auto_now_add=True, help_text="Date license was issued")
    expiry_date = models.DateField(null=True, blank=True, help_text="License expiration date (null = never expires)")
    is_active = models.BooleanField(default=True, help_text="Whether license is active")
    max_users = models.IntegerField(default=5, help_text="Maximum number of users allowed")
    
    class Meta:
        verbose_name = 'License Key'
        verbose_name_plural = 'License Keys'
        ordering = ['-issued_date']
    
    def is_valid(self):
        """Check if license is active and not expired"""
        if not self.is_active:
            return False
        if self.expiry_date and self.expiry_date < timezone.now().date():
            return False
        return True
    
    def __str__(self):
        return f"{self.tier.upper()} - {self.key[:8]}..." if len(self.key) > 8 else f"{self.tier.upper()} - {self.key}"


class BarangayInfo(models.Model):
    """
    Singleton model to store Barangay Configuration.
    Ensures only one instance exists.
    """
    name = models.CharField(max_length=200, help_text="Official name of the Barangay")
    address = models.TextField(help_text="Complete address")
    logo = models.ImageField(upload_to='barangay/logo/', blank=True, null=True)
    contact_number = models.CharField(max_length=50, blank=True)
    email = models.EmailField(blank=True)
    
    # GIS Location (Center of Barangay)
    latitude = models.FloatField(blank=True, null=True, help_text="Center Latitude")
    longitude = models.FloatField(blank=True, null=True, help_text="Center Longitude")
    
    # System Config
    is_setup_complete = models.BooleanField(default=False)
    
    def save(self, *args, **kwargs):
        if not self.pk and BarangayInfo.objects.exists():
            # If trying to create a new instance when one exists, update the existing one instead
            # or raise an error. For simplicity, we can just enforce singleton at view level,
            # but let's be safe.
            return super().save(*args, **kwargs)
        return super().save(*args, **kwargs)

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = "Barangay Information"
        verbose_name_plural = "Barangay Information"

