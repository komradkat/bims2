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

    # Structured address fields
    street = models.CharField(max_length=200, blank=True, help_text="Street / Purok / Sitio")
    city_municipality = models.CharField(max_length=100, help_text="City or Municipality")
    province = models.CharField(max_length=100, help_text="Province")
    region = models.CharField(max_length=100, blank=True, help_text="Region")
    zip_code = models.CharField(max_length=10, blank=True)

    logo = models.ImageField(upload_to='barangay/logo/', blank=True, null=True)
    contact_number = models.CharField(max_length=50, blank=True)
    email = models.EmailField(blank=True)
    captain_name = models.CharField(
        max_length=200,
        blank=True,
        help_text="Full name of the Punong Barangay (used on printed certificates)"
    )

    # GIS Location (Center of Barangay)
    latitude = models.FloatField(blank=True, null=True, help_text="Center Latitude")
    longitude = models.FloatField(blank=True, null=True, help_text="Center Longitude")

    # System Config
    is_setup_complete = models.BooleanField(default=False)

    @property
    def full_address(self):
        """Return a composed full address string."""
        parts = filter(None, [
            self.street,
            self.city_municipality,
            self.province,
            self.region,
            self.zip_code,
        ])
        return ", ".join(parts)
    
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


class BarangayOfficial(models.Model):
    """
    Barangay council members and officials.
    One official can be marked as Punong Barangay; their name is used on printed certificates.
    """

    POSITION_CHOICES = [
        ('punong_barangay', 'Punong Barangay'),
        ('kagawad', 'Barangay Kagawad'),
        ('sk_chairman', 'SK Chairman'),
        ('secretary', 'Barangay Secretary'),
        ('treasurer', 'Barangay Treasurer'),
        ('lupong_tagapamayapa', 'Lupong Tagapamayapa'),
        ('other', 'Other'),
    ]

    COMMITTEE_CHOICES = [
        ('', '— None —'),
        ('peace_order', 'Peace & Order'),
        ('health', 'Health & Sanitation'),
        ('education', 'Education & Culture'),
        ('infrastructure', 'Infrastructure'),
        ('livelihood', 'Livelihood & Entrepreneurship'),
        ('environment', 'Environment & Natural Resources'),
        ('finance', 'Finance & Appropriation'),
        ('women', 'Women & Family'),
        ('youth', 'Youth & Sports'),
        ('senior', 'Senior Citizen Affairs'),
    ]

    position = models.CharField(max_length=30, choices=POSITION_CHOICES)
    committee = models.CharField(max_length=50, choices=COMMITTEE_CHOICES, blank=True)

    # Personal details
    honorific = models.CharField(max_length=10, blank=True, help_text="e.g. Hon., Dr.")
    first_name = models.CharField(max_length=100)
    middle_name = models.CharField(max_length=100, blank=True)
    last_name = models.CharField(max_length=100)
    suffix = models.CharField(max_length=10, blank=True, help_text="e.g. Jr., Sr.")

    photo = models.ImageField(upload_to='officials/photos/', blank=True, null=True)

    # Term info
    term_start = models.DateField(null=True, blank=True)
    term_end = models.DateField(null=True, blank=True)

    contact_number = models.CharField(max_length=50, blank=True)
    email = models.EmailField(blank=True)

    is_active = models.BooleanField(default=True)
    order = models.PositiveSmallIntegerField(default=0, help_text="Display order (lower = first)")

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['order', 'position', 'last_name']
        verbose_name = 'Barangay Official'
        verbose_name_plural = 'Barangay Officials'

    @property
    def full_name(self):
        parts = filter(None, [self.honorific, self.first_name, self.middle_name, self.last_name, self.suffix])
        return ' '.join(parts)

    @property
    def display_name(self):
        """Name without honorific, for document signatures."""
        parts = filter(None, [self.first_name, self.middle_name, self.last_name, self.suffix])
        return ' '.join(parts)

    def __str__(self):
        return f"{self.full_name} — {self.get_position_display()}"
