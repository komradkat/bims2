from django.test import TestCase
from .models import BusinessPermit
from django.utils import timezone

class BusinessPermitTests(TestCase):
    def test_create_permit(self):
        permit = BusinessPermit.objects.create(
            business_name="Test Business",
            owner_name="Juan Dela Cruz",
            address="123 Test St",
            expiration_date=timezone.now().date()
        )
        self.assertEqual(permit.business_name, "Test Business")
        self.assertTrue(permit.permit_number.startswith("BP-"))
