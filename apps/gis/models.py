from django.db import models

class EmergencyService(models.Model):
    SERVICE_TYPES = [
        ('police', 'Police Station'),
        ('fire', 'Fire Station'),
        ('hospital', 'Hospital / Clinic'),
    ]

    name = models.CharField(max_length=200)
    service_type = models.CharField(max_length=20, choices=SERVICE_TYPES)
    address = models.TextField(blank=True)
    contact_number = models.CharField(max_length=50, blank=True)
    
    latitude = models.FloatField()
    longitude = models.FloatField()
    
    osm_id = models.BigIntegerField(unique=True, null=True, blank=True, db_index=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = 'Emergency Service'
        verbose_name_plural = 'Emergency Services'
        ordering = ['service_type', 'name']

    def __str__(self):
        return f"{self.name} ({self.get_service_type_display()})"
