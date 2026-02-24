# Residents models
from django.db import models
from django.core.exceptions import ValidationError
from django.core.validators import RegexValidator, MinValueValidator
from simple_history.models import HistoricalRecords

# Security: File upload limits
MAX_UPLOAD_SIZE = 2 * 1024 * 1024  # 2MB
ALLOWED_IMAGE_TYPES = ['image/jpeg', 'image/png']


from django.utils.text import slugify


class Purok(models.Model):
    """
    Standardizes the Puroks/Sitios in the Barangay.
    Used for dropdown choices in forms.
    """
    name = models.CharField(max_length=100, unique=True)
    description = models.TextField(blank=True)
    slug = models.SlugField(max_length=100, unique=True, blank=True)
    
    class Meta:
        ordering = ['name']
        verbose_name = "Purok"
        verbose_name_plural = "Puroks"
        
    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)
            
    def __str__(self):
        return self.name


class Resident(models.Model):
    """
    Main resident model storing all personal, contact, and sectoral information.
    """
    
    # Choices
    SEX_CHOICES = [
        ('M', 'Male'),
        ('F', 'Female'),
    ]
    
    CIVIL_STATUS_CHOICES = [
        ('single', 'Single'),
        ('married', 'Married'),
        ('widowed', 'Widowed'),
        ('separated', 'Separated'),
    ]
    
    BLOOD_TYPE_CHOICES = [
        ('A+', 'A+'),
        ('A-', 'A-'),
        ('B+', 'B+'),
        ('B-', 'B-'),
        ('AB+', 'AB+'),
        ('AB-', 'AB-'),
        ('O+', 'O+'),
        ('O-', 'O-'),
    ]
    
    EDUCATIONAL_ATTAINMENT_CHOICES = [
        ('elementary_level', 'Elementary Level'),
        ('elementary_graduate', 'Elementary Graduate'),
        ('high_school_level', 'High School Level'),
        ('high_school_graduate', 'High School Graduate'),
        ('college_level', 'College Level'),
        ('college_graduate', 'College Graduate'),
        ('vocational', 'Vocational'),
        ('post_graduate', 'Post-Graduate'),
    ]
    
    EMPLOYMENT_STATUS_CHOICES = [
        ('employed', 'Employed'),
        ('unemployed', 'Unemployed'),
        ('self_employed', 'Self-Employed'),
        ('student', 'Student'),
        ('retired', 'Retired'),
    ]
    
    # Personal Information
    first_name = models.CharField(max_length=100)
    middle_name = models.CharField(max_length=100, blank=True)
    last_name = models.CharField(max_length=100)
    suffix = models.CharField(max_length=10, blank=True, help_text="e.g. Jr., Sr., III")
    
    date_of_birth = models.DateField()
    sex = models.CharField(max_length=1, choices=SEX_CHOICES)
    civil_status = models.CharField(max_length=20, choices=CIVIL_STATUS_CHOICES)
    citizenship = models.CharField(max_length=50, default='Filipino')
    
    place_of_birth = models.CharField(max_length=200, blank=True)
    religion = models.CharField(max_length=100, blank=True)
    blood_type = models.CharField(max_length=3, choices=BLOOD_TYPE_CHOICES, blank=True)
    
    # Education & Employment
    educational_attainment = models.CharField(
        max_length=50,
        choices=EDUCATIONAL_ATTAINMENT_CHOICES,
        blank=True
    )
    employment_status = models.CharField(
        max_length=20,
        choices=EMPLOYMENT_STATUS_CHOICES,
        blank=True
    )
    occupation = models.CharField(max_length=200, blank=True)
    
    # Contact Information
    mobile_number = models.CharField(
        max_length=20,
        blank=True,
        validators=[RegexValidator(
            regex=r'^\+?1?\d{9,15}$',
            message="Phone number must be entered in the format: '+999999999'. Up to 15 digits allowed."
        )]
    )
    email = models.EmailField(blank=True)
    
    # Government IDs
    philhealth_no = models.CharField(max_length=20, blank=True, verbose_name="PhilHealth Number")
    sss_gsis_no = models.CharField(max_length=20, blank=True, verbose_name="SSS/GSIS Number")
    tin_no = models.CharField(max_length=20, blank=True, verbose_name="TIN Number")
    
    # Emergency Contact
    emergency_contact_name = models.CharField(max_length=200, blank=True)
    emergency_contact_number = models.CharField(max_length=20, blank=True)
    
    # Residence Information
    purok = models.CharField(max_length=100, help_text="Purok/Sitio")
    purok_link = models.ForeignKey(
        'Purok', 
        on_delete=models.SET_NULL, 
        null=True, 
        blank=True, 
        related_name='residents',
        help_text="Formal link to Purok table"
    )
    address = models.CharField(max_length=500, help_text="House Number/Street")
    years_of_residency = models.PositiveIntegerField(default=0, blank=True)
    
    # Household Information
    is_household_head = models.BooleanField(default=True)
    household_head = models.ForeignKey(
        'self',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='household_members',
        help_text="Leave blank if this person is the household head"
    )
    relationship_to_head = models.CharField(
        max_length=50,
        blank=True,
        help_text="Relationship to household head (if not head)"
    )
    
    # Sectoral Information
    is_senior_citizen = models.BooleanField(default=False)
    is_pwd = models.BooleanField(default=False, verbose_name="Is PWD")
    disability_type = models.CharField(max_length=200, blank=True)
    is_solo_parent = models.BooleanField(default=False)
    is_4ps = models.BooleanField(default=False, verbose_name="Is 4Ps Member")
    is_indigent = models.BooleanField(default=False)
    is_voter = models.BooleanField(default=False)
    precinct_number = models.CharField(max_length=20, blank=True)
    
    # Photo
    photo = models.ImageField(upload_to='residents/photos/', blank=True, null=True)
    
    def clean(self):
        super().clean()
        if self.photo and self.photo.size > MAX_UPLOAD_SIZE:
            raise ValidationError({'photo': f"Image file too large. Max size is {MAX_UPLOAD_SIZE/1024/1024}MB."})
        
        # Security & Business Logic: Senior Citizen validation
        if self.date_of_birth and self.is_senior_citizen:
            from datetime import date
            today = date.today()
            age = today.year - self.date_of_birth.year - (
                (today.month, today.day) < (self.date_of_birth.month, self.date_of_birth.day)
            )
            if age < 60:
                raise ValidationError({
                    'is_senior_citizen': 'Person must be 60 years or older to be marked as Senior Citizen.'
                })

        # Security & Business Logic: PWD validation
        if self.is_pwd and not self.disability_type:
            raise ValidationError({
                'disability_type': 'Please specify the disability type for PWD.'
            })

        # Security & Business Logic: Voter validation
        if self.is_voter and not self.precinct_number:
            raise ValidationError({
                'precinct_number': 'Please provide the precinct number for registered voters.'
            })
    
    # Metadata
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    is_active = models.BooleanField(default=True, help_text="Set to False for deceased or moved out")

    # GIS Location
    latitude = models.FloatField(blank=True, null=True, help_text="Latitude coordinate")
    longitude = models.FloatField(blank=True, null=True, help_text="Longitude coordinate")
    
    # Audit Trail
    history = HistoricalRecords()
    
    class Meta:
        ordering = ['last_name', 'first_name']
        indexes = [
            models.Index(fields=['last_name', 'first_name']),
            models.Index(fields=['purok']),
            models.Index(fields=['is_active']),
        ]
        verbose_name = 'Resident'
        verbose_name_plural = 'Residents'
    
    @classmethod
    def get_purok_choices(cls):
        """Returns a list of tuples for form choices from the Purok model."""
        return [(p.name, p.name) for p in Purok.objects.all()]

    def __str__(self):
        middle_initial = f"{self.middle_name[0]}." if self.middle_name else ""
        suffix = f" {self.suffix}" if self.suffix else ""
        return f"{self.last_name}, {self.first_name} {middle_initial}{suffix}".strip()
    
    @property
    def full_name(self):
        """Returns the full name in 'First Middle Last Suffix' format"""
        parts = [self.first_name]
        if self.middle_name:
            parts.append(self.middle_name)
        parts.append(self.last_name)
        if self.suffix:
            parts.append(self.suffix)
        return " ".join(parts)
    
    @property
    def age(self):
        """Calculate age from date of birth"""
        from datetime import date
        today = date.today()
        return today.year - self.date_of_birth.year - (
            (today.month, today.day) < (self.date_of_birth.month, self.date_of_birth.day)
        )
    
    @property
    def sectors(self):
        """Returns a list of sectors this resident belongs to"""
        sectors = []
        if self.is_senior_citizen:
            sectors.append('Senior Citizen')
        if self.is_pwd:
            sectors.append('PWD')
        if self.is_solo_parent:
            sectors.append('Solo Parent')
        if self.is_4ps:
            sectors.append('4Ps')
        if self.is_indigent:
            sectors.append('Indigent')
        if self.is_voter:
            sectors.append('Voter')
        return sectors


class HouseholdMember(models.Model):
    """
    Explicit household membership model for tracking family relationships.
    This is an alternative/supplementary approach to the self-referential household_head field.
    """
    
    RELATIONSHIP_CHOICES = [
        ('head', 'Household Head'),
        ('spouse', 'Spouse'),
        ('son', 'Son'),
        ('daughter', 'Daughter'),
        ('parent', 'Parent'),
        ('sibling', 'Sibling'),
        ('in_law', 'In-Law'),
        ('grandchild', 'Grandchild'),
        ('grandparent', 'Grandparent'),
        ('other_relative', 'Other Relative'),
        ('boarder', 'Boarder/Helper'),
    ]
    
    household_head = models.ForeignKey(
        Resident,
        on_delete=models.CASCADE,
        related_name='household_membership_as_head'
    )
    member = models.ForeignKey(
        Resident,
        on_delete=models.CASCADE,
        related_name='household_membership_as_member'
    )
    relationship = models.CharField(max_length=20, choices=RELATIONSHIP_CHOICES)
    
    created_at = models.DateTimeField(auto_now_add=True)
    
    # Audit Trail
    history = HistoricalRecords()
    
    class Meta:
        unique_together = ['household_head', 'member']
        verbose_name = 'Household Member'
        verbose_name_plural = 'Household Members'
    
    def __str__(self):
        return f"{self.member} - {self.get_relationship_display()} of {self.household_head}"
