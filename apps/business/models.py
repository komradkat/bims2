from django.db import models
from django.conf import settings
from simple_history.models import HistoricalRecords
from django.utils import timezone

class BusinessPermit(models.Model):
    STATUS_CHOICES = [
        ('active', 'Active'),
        ('expired', 'Expired'),
        ('pending', 'Pending'),
        ('cancelled', 'Cancelled'),
    ]

    business_name = models.CharField(max_length=255)
    owner_name = models.CharField(max_length=255)
    owner_address = models.TextField(blank=True)

    address = models.TextField(blank=True, verbose_name="Business Address")
    contact_number = models.CharField(max_length=20, blank=True)
    email = models.EmailField(blank=True)

    # Registration Details
    permit_number = models.CharField(max_length=50, unique=True, blank=True)
    dti_sec_number = models.CharField(max_length=50, blank=True, verbose_name="DTI/SEC Registration Number")
    tin = models.CharField(max_length=50, blank=True, verbose_name="TIN")
    nature_of_business = models.CharField(max_length=100, blank=True)

    # Cedula Details
    cedula_number = models.CharField(max_length=50, blank=True)
    cedula_date = models.DateField(null=True, blank=True)

    # Financials
    gross_sales = models.DecimalField(max_digits=12, decimal_places=2, default=0.00)
    clearance_fee = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    or_number = models.CharField(max_length=50, blank=True)

    issued_date = models.DateField(default=timezone.now)
    expiration_date = models.DateField()
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    created_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, related_name='issued_permits')

    history = HistoricalRecords()

    class Meta:
        ordering = ['-expiration_date']
        verbose_name = "Business Permit"
        verbose_name_plural = "Business Permits"

    def __str__(self):
        return f"{self.business_name} ({self.permit_number})"

    def save(self, *args, **kwargs):
        if not self.permit_number:
            # Generate permit number: BP-YYYY-XXXX
            year = timezone.now().year
            last_permit = BusinessPermit.objects.filter(permit_number__startswith=f'BP-{year}').order_by('permit_number').last()
            if last_permit:
                try:
                    last_number = int(last_permit.permit_number.split('-')[-1])
                    new_number = last_number + 1
                except ValueError:
                    new_number = 1
            else:
                new_number = 1
            self.permit_number = f'BP-{year}-{new_number:04d}'

        # Auto-set expiration to end of year if not set
        if not self.expiration_date:
            year = self.issued_date.year
            self.expiration_date = timezone.datetime(year, 12, 31).date()

        super().save(*args, **kwargs)

    @property
    def is_expired(self):
        return self.expiration_date < timezone.now().date()

    @property
    def status_color(self):
        if self.status == 'active':
            return 'success'
        elif self.status == 'expired':
            return 'error'
        elif self.status == 'pending':
            return 'warning'
        else:
            return 'ghost'

class BusinessClearance(models.Model):
    """
    Record of issued business clearances.
    """
    permit = models.ForeignKey(BusinessPermit, on_delete=models.CASCADE, related_name='clearances')
    or_number = models.CharField(max_length=50)
    amount_paid = models.DecimalField(max_digits=10, decimal_places=2)
    issued_date = models.DateTimeField(auto_now_add=True)
    issued_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True)

    history = HistoricalRecords()

    def __str__(self):
        return f"Clearance for {self.permit.business_name} - {self.issued_date.strftime('%Y-%m-%d')}"
