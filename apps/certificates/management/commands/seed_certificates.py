from django.core.management.base import BaseCommand
from apps.certificates.models import CertificateType


class Command(BaseCommand):
    help = 'Seeds the database with standard certificate types'

    def handle(self, *args, **options):
        certificate_types = [
            {
                'name': 'Barangay Clearance',
                'slug': 'barangay-clearance',
                'tier': 'community',
                'description': 'Certificate of Barangay Clearance for various purposes',
                'default_price': 50.00,
                'template_file': 'certificates/print/clearance.html',
            },
            {
                'name': 'Certificate of Indigency',
                'slug': 'indigency',
                'tier': 'community',
                'description': 'Certificate for indigent residents to avail of social services',
                'default_price': 0.00,
                'template_file': 'certificates/print/indigency.html',
            },
            {
                'name': 'Certificate of Residency',
                'slug': 'residency',
                'tier': 'community',
                'description': 'Proof of residence for various legal requirements',
                'default_price': 50.00,
                'template_file': 'certificates/print/residency.html',
            },
            {
                'name': 'Business Clearance',
                'slug': 'business-clearance',
                'tier': 'pro',
                'description': 'Prerequisite for Mayor\'s Permit and business operations',
                'default_price': 200.00,
                'template_file': 'certificates/print/business_clearance.html',
            },
            {
                'name': 'Certificate of Good Moral',
                'slug': 'good-moral',
                'tier': 'pro',
                'description': 'Certification of good character and law-abiding standing',
                'default_price': 50.00,
                'template_file': 'certificates/print/good_moral.html',
            },
            {
                'name': 'First Time Job Seeker',
                'slug': 'job-seeker',
                'tier': 'pro',
                'description': 'RA 11261 - Free certification for first-time job applicants',
                'default_price': 0.00,
                'template_file': 'certificates/print/job_seeker.html',
            },
        ]

        created_count = 0
        updated_count = 0

        for cert_data in certificate_types:
            cert_type, created = CertificateType.objects.update_or_create(
                slug=cert_data['slug'],
                defaults=cert_data
            )
            if created:
                created_count += 1
                self.stdout.write(
                    self.style.SUCCESS(f'Created: {cert_type.name}')
                )
            else:
                updated_count += 1
                self.stdout.write(
                    self.style.WARNING(f'Updated: {cert_type.name}')
                )

        self.stdout.write(
            self.style.SUCCESS(
                f'\nSeeding complete! Created: {created_count}, Updated: {updated_count}'
            )
        )
