from django.core.management.base import BaseCommand
from apps.certificates.models import CertificateType


class Command(BaseCommand):
    help = "Seed default certificate types"

    def handle(self, *args, **kwargs):
        self.stdout.write("Seeding certificate types...")

        certs = [
            # Community (Free/Basic)
            {
                "name": "Certificate of Indigency",
                "slug": "indigency",
                "tier": "community",
                "price": 0.00,
                "template": "certificates/print/indigency.html",
            },
            {
                "name": "Certificate of Residency",
                "slug": "residency",
                "tier": "community",
                "price": 50.00,
                "template": "certificates/print/residency.html",
            },
            {
                "name": "First-Time Jobseeker Oath",
                "slug": "jobseeker",
                "tier": "community",
                "price": 0.00,
                "template": "certificates/print/jobseeker.html",
            },
            # Pro (Business/Legal)
            {
                "name": "Barangay Clearance",
                "slug": "clearance",
                "tier": "pro",
                "price": 100.00,
                "template": "certificates/print/clearance.html",
            },
            {
                "name": "Business Permit",
                "slug": "business-permit",
                "tier": "pro",
                "price": 500.00,
                "template": "certificates/print/business_permit.html",
            },
            {
                "name": "Certificate of Good Moral",
                "slug": "good-moral",
                "tier": "pro",
                "price": 75.00,
                "template": "certificates/print/good_moral.html",
            },
            # Ultra (Specialized)
            {
                "name": "Special Permit",
                "slug": "special-permit",
                "tier": "ultra",
                "price": 200.00,
                "template": "certificates/print/special.html",
            },
        ]

        for c in certs:
            obj, created = CertificateType.objects.update_or_create(
                slug=c["slug"],
                defaults={
                    "name": c["name"],
                    "tier": c["tier"],
                    "default_price": c["price"],
                    "template_file": c["template"],
                },
            )
            status = "Created" if created else "Updated"
            self.stdout.write(f" - {status}: {obj.name} ({obj.tier})")

        self.stdout.write(self.style.SUCCESS("Certificate types seeded successfully."))
