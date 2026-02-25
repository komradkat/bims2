from django.db import models
from django.conf import settings
from django.core.validators import MinValueValidator
from simple_history.models import HistoricalRecords


class Fee(models.Model):
    name = models.CharField(max_length=100)
    description = models.TextField(blank=True)
    default_amount = models.DecimalField(
        max_digits=10, decimal_places=2, default=0.00, validators=[MinValueValidator(0)]
    )

    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.name} (₱{self.default_amount})"


class OfficialReceipt(models.Model):
    STATUS_CHOICES = [
        ("paid", "Paid"),
        ("cancelled", "Cancelled"),
    ]

    or_number = models.CharField(max_length=50, unique=True)
    payor = models.CharField(max_length=255)
    particulars = models.TextField(help_text="Description of payment")
    amount = models.DecimalField(
        max_digits=10, decimal_places=2, validators=[MinValueValidator(0)]
    )
    date = models.DateTimeField(auto_now_add=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default="paid")

    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True
    )

    history = HistoricalRecords()

    class Meta:
        ordering = ["-date"]
        verbose_name = "Official Receipt"
        verbose_name_plural = "Official Receipts"

    def __str__(self):
        return f"OR# {self.or_number} - {self.payor} (₱{self.amount})"
