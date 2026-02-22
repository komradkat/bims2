"""
Data migration: seed all CertificateType records from Tiers.md definitions.
This ensures certificate types are always present even after a DB reset.
"""
from django.db import migrations


CERTIFICATE_TYPES = [
    # Community Tier — always free, included in all editions
    {
        'name': 'Certificate of Indigency',
        'slug': 'indigency',
        'tier': 'community',
        'description': 'For residents seeking financial assistance, medical aid (DSWD/PAO), or scholarship requirements.',
        'default_price': '0.00',
        'template_file': 'certificates/print/indigency.html',
        'is_active': True,
    },
    {
        'name': 'Certificate of Residency',
        'slug': 'residency',
        'tier': 'community',
        'description': 'Proof of residence for bank applications, school enrollment, or local ID requirements.',
        'default_price': '0.00',
        'template_file': 'certificates/print/residency.html',
        'is_active': True,
    },
    {
        'name': 'First-Time Jobseeker Certification',
        'slug': 'jobseeker',
        'tier': 'community',
        'description': '(RA 11261) Free certification for first-time job applicants to waive national government fees.',
        'default_price': '0.00',
        'template_file': 'certificates/print/jobseeker.html',
        'is_active': True,
    },
    # Pro Tier — revenue-generating documents
    {
        'name': 'Barangay Clearance',
        'slug': 'clearance',
        'tier': 'pro',
        'description': 'Standard clearance for employment, business registration, or other legal purposes.',
        'default_price': '50.00',
        'template_file': 'certificates/print/clearance.html',
        'is_active': True,
    },
    {
        'name': 'Certificate of Good Moral Character',
        'slug': 'good-moral',
        'tier': 'pro',
        'description': 'Certification of good standing and no derogatory record in the community.',
        'default_price': '30.00',
        'template_file': 'certificates/print/good_moral.html',
        'is_active': True,
    },
    {
        'name': 'Barangay Business Clearance',
        'slug': 'business-permit',
        'tier': 'pro',
        'description': 'Official permit to operate a business within the Barangay jurisdiction.',
        'default_price': '150.00',
        'template_file': 'certificates/print/business_permit.html',
        'is_active': True,
    },
    # Ultra Tier — advanced / QR-verified
    {
        'name': 'Special Permit',
        'slug': 'special-permit',
        'tier': 'ultra',
        'description': 'For special activities, construction, or other specific Barangay transactional needs.',
        'default_price': '100.00',
        'template_file': 'certificates/print/special_permit.html',
        'is_active': True,
    },
]


def seed_certificate_types(apps, schema_editor):
    CertificateType = apps.get_model('certificates', 'CertificateType')
    for cert in CERTIFICATE_TYPES:
        CertificateType.objects.update_or_create(
            slug=cert['slug'],
            defaults=cert,
        )


def unseed_certificate_types(apps, schema_editor):
    """Reverse: remove only the seeded slugs."""
    CertificateType = apps.get_model('certificates', 'CertificateType')
    slugs = [c['slug'] for c in CERTIFICATE_TYPES]
    CertificateType.objects.filter(slug__in=slugs).delete()


class Migration(migrations.Migration):

    dependencies = [
        ('certificates', '0002_certificatetype_tier'),
    ]

    operations = [
        migrations.RunPython(seed_certificate_types, unseed_certificate_types),
    ]
