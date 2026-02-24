from django.db import models
from django.conf import settings
from django.utils import timezone
from django.core.exceptions import ValidationError
from apps.residents.models import Resident
from simple_history.models import HistoricalRecords


class BlotterCase(models.Model):
    STATUS_CHOICES = [
        ('mediation', 'Mediation'),
        ('conciliation', 'Conciliation'),
        ('arbitration', 'Arbitration'),
        ('settled', 'Settled'),
        ('dismissed', 'Dismissed'),
        ('cfa', 'Certified to File Action'),
    ]

    INCIDENT_TYPES = [
        ('physical_injury', 'Physical Injury'),
        ('theft', 'Theft'),
        ('slander', 'Slander/Oral Defamation'),
        ('boundary_dispute', 'Boundary Dispute'),
        ('debt_collection', 'Debt Collection'),
        ('threats', 'Threats'),
        ('scam', 'Estafa/Scam'),
        ('others', 'Others'),
    ]

    case_number = models.CharField(max_length=20, unique=True, editable=False)
    incident_type = models.CharField(max_length=50, choices=INCIDENT_TYPES)
    incident_date = models.DateTimeField()
    incident_location = models.CharField(max_length=255)
    narrative = models.TextField()
    
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='mediation')
    
    settlement_details = models.TextField(blank=True, help_text="Terms of agreement if settled")
    dismissal_reason = models.TextField(blank=True, help_text="Reason for dismissal")
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    created_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True)
    
    history = HistoricalRecords()

    @property
    def participants_display(self):
        complainants = self.complainants.all()
        respondents = self.respondents.all()
        
        c_names = [str(c) for c in complainants]
        r_names = [str(r) for r in respondents]
        
        c_str = ", ".join(c_names) if c_names else "Unknown"
        r_str = ", ".join(r_names) if r_names else "Unknown"
        
        return f"{c_str} vs. {r_str}"

    @property
    def status_color(self):
        colors = {
            'mediation': 'warning',
            'conciliation': 'info',
            'arbitration': 'secondary',
            'settled': 'success',
            'dismissed': 'ghost',
            'cfa': 'error',
        }
        return colors.get(self.status, 'ghost')

    @property
    def next_hearing(self):
        from django.utils import timezone
        return self.hearings.filter(
            status='scheduled', 
            scheduled_at__gte=timezone.now()
        ).first()

    class Meta:
        ordering = ['-created_at']
        verbose_name = "Blotter Case"
        verbose_name_plural = "Blotter Cases"

    def __str__(self):
        return f"{self.case_number} - {self.get_incident_type_display()}"

    def save(self, *args, **kwargs):
        if not self.case_number:
            # Generate case number: BCC-YYYY-0001
            year = timezone.now().year
            last_case = BlotterCase.objects.filter(case_number__startswith=f'BCC-{year}').order_by('case_number').last()
            if last_case:
                last_number = int(last_case.case_number.split('-')[-1])
                new_number = last_number + 1
            else:
                new_number = 1
            self.case_number = f'BCC-{year}-{new_number:04d}'
        super().save(*args, **kwargs)


class Complainant(models.Model):
    case = models.ForeignKey(BlotterCase, on_delete=models.CASCADE, related_name='complainants')
    resident = models.ForeignKey(Resident, on_delete=models.SET_NULL, null=True, blank=True, related_name='complaints_filed')
    # For non-residents
    name = models.CharField(max_length=255, blank=True, help_text="Full name (if not a resident)")
    address = models.CharField(max_length=255, blank=True, help_text="Address (if not a resident)")
    contact_number = models.CharField(max_length=20, blank=True)

    def clean(self):
        super().clean()
        if not self.resident and not self.name:
            raise ValidationError("Either a resident must be selected or a name must be provided for non-residents.")
        if not self.resident and not self.address:
             raise ValidationError("Address is required for non-resident complainants.")

    def __str__(self):
        if self.resident:
            return f"{self.resident.full_name} (Resident)"
        return f"{self.name} (Non-Resident)"


class Respondent(models.Model):
    case = models.ForeignKey(BlotterCase, on_delete=models.CASCADE, related_name='respondents')
    resident = models.ForeignKey(Resident, on_delete=models.SET_NULL, null=True, blank=True, related_name='complaints_received')
    # For non-residents
    name = models.CharField(max_length=255, blank=True, help_text="Full name (if not a resident)")
    address = models.CharField(max_length=255, blank=True, help_text="Address (if not a resident)")
    contact_number = models.CharField(max_length=20, blank=True)

    def clean(self):
        super().clean()
        if not self.resident and not self.name:
            raise ValidationError("Either a resident must be selected or a name must be provided for non-residents.")

    def __str__(self):
        if self.resident:
            return f"{self.resident.full_name} (Resident)"
        return f"{self.name} (Non-Resident)"


class Hearing(models.Model):
    HEARING_STATUS = [
        ('scheduled', 'Scheduled'),
        ('completed', 'Completed'),
        ('cancelled', 'Cancelled'),
        ('no_show', 'No Show'),
    ]

    case = models.ForeignKey(BlotterCase, on_delete=models.CASCADE, related_name='hearings')
    scheduled_at = models.DateTimeField()
    status = models.CharField(max_length=20, choices=HEARING_STATUS, default='scheduled')
    remarks = models.TextField(blank=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['scheduled_at']

    def __str__(self):
        return f"Hearing for {self.case.case_number} on {self.scheduled_at}"
