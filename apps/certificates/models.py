from django.db import models
from django.conf import settings
from simple_history.models import HistoricalRecords
from apps.residents.models import Resident

class CertificateType(models.Model):
    """
    Defines the types of certificates available for issuance.
    """
    TIER_CHOICES = [
        ('community', 'Community (Free/Basic)'),
        ('pro', 'Pro (Advanced)'),
        ('ultra', 'Ultra (Premium/GIS)'),
    ]

    name = models.CharField(max_length=100)
    slug = models.SlugField(unique=True)
    tier = models.CharField(max_length=20, choices=TIER_CHOICES, default='community')
    description = models.TextField(blank=True)
    default_price = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    template_file = models.CharField(
        max_length=255, 
        help_text="Path to the HTML template for this certificate (e.g., 'certificates/print/clearance.html')"
    )
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name

class Certificate(models.Model):
    """
    Record of an issued certificate.
    """
    STATUS_CHOICES = [
        ('pending', 'Pending Payment'),
        ('paid', 'Paid'),
        ('issued', 'Issued'),
        ('cancelled', 'Cancelled'),
    ]

    transaction_number = models.CharField(max_length=20, unique=True, editable=False)
    resident = models.ForeignKey(Resident, on_delete=models.CASCADE, related_name='certificates')
    certificate_type = models.ForeignKey(CertificateType, on_delete=models.PROTECT)
    
    # Transaction Details
    purpose = models.TextField(help_text="Reason for requesting the certificate")
    or_number = models.CharField(max_length=50, blank=True, help_text="Official Receipt Number")
    amount_paid = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    
    # Metadata
    issued_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True)
    issued_at = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    history = HistoricalRecords()

    def save(self, *args, **kwargs):
        if not self.transaction_number:
            # Generate a simple transaction number (e.g., CERT-YYYYMMDD-XXXX)
            import datetime
            import random
            today = datetime.date.today().strftime('%Y%m%d')
            rand = random.randint(1000, 9999)
            self.transaction_number = f"CERT-{today}-{rand}"
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.certificate_type.name} - {self.resident.full_name}"
