"""
Management command to generate test license keys for development.
"""

from django.core.management.base import BaseCommand
from apps.core.models import LicenseKey
import secrets
import string
from datetime import date, timedelta


class Command(BaseCommand):
    help = "Generate test license keys for development"

    def add_arguments(self, parser):
        parser.add_argument(
            "--tier",
            type=str,
            choices=["community", "pro", "ultra"],
            default="ultra",
            help="License tier to generate",
        )
        parser.add_argument(
            "--count", type=int, default=1, help="Number of licenses to generate"
        )
        parser.add_argument(
            "--days",
            type=int,
            default=365,
            help="Number of days until expiry (0 for no expiry)",
        )

    def handle(self, *args, **options):
        tier = options["tier"]
        count = options["count"]
        days = options["days"]

        max_users_map = {
            "community": 5,
            "pro": 20,
            "ultra": 100,
        }

        self.stdout.write(f"\nGenerating {count} {tier.upper()} license key(s)...\n")

        for i in range(count):
            # Generate random license key
            key = self.generate_license_key()

            # Calculate expiry date
            expiry_date = None
            if days > 0:
                expiry_date = date.today() + timedelta(days=days)

            # Create license
            LicenseKey.objects.create(
                key=key,
                tier=tier,
                max_users=max_users_map[tier],
                expiry_date=expiry_date,
                is_active=True,
            )

            self.stdout.write(
                self.style.SUCCESS(f"✓ Created {tier.upper()} license: {key}")
            )
            if expiry_date:
                self.stdout.write(f"  Expires: {expiry_date}")
            else:
                self.stdout.write("  Expires: Never")
            self.stdout.write(f"  Max Users: {max_users_map[tier]}\n")

        self.stdout.write(
            self.style.SUCCESS(f"\n✓ Successfully generated {count} license key(s)!")
        )
        self.stdout.write("\nTo activate, go to: /license/activate/\n")

    def generate_license_key(self):
        """Generate a random license key in format: XXXX-XXXX-XXXX-XXXX-XXXX"""
        chars = string.ascii_uppercase + string.digits
        segments = []
        for _ in range(5):
            segment = "".join(secrets.choice(chars) for _ in range(4))
            segments.append(segment)
        return "-".join(segments)
