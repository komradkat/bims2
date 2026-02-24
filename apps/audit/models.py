from django.db import models
from django.conf import settings

# Create your models here.

class SystemLog(models.Model):
    ACTION_CHOICES = [
        ('LOGIN', 'User Login'),
        ('LOGOUT', 'User Logout'),
        ('DATA_EXPORT', 'Data Export'),
        ('SETUP_STEP', 'Setup Step Completed'),
        ('INITIALIZE', 'System Initialized'),
        ('LICENSE_ACTIVATE', 'License Activated'),
        ('PERMISSION_DENIED', 'Permission Denied'),
        ('CRITICAL_ERROR', 'Critical System Error'),
    ]

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL, 
        on_delete=models.SET_NULL, 
        null=True, 
        blank=True,
        related_name='system_logs'
    )
    action = models.CharField(max_length=50, choices=ACTION_CHOICES)
    details = models.JSONField(default=dict, blank=True)
    ip_address = models.GenericIPAddressField(null=True, blank=True)
    timestamp = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-timestamp']
        verbose_name = 'System Log'
        verbose_name_plural = 'System Logs'

    def __str__(self):
        user_str = self.user.username if self.user else "System"
        return f"{self.timestamp} - {user_str} - {self.action}"
