from django.core.management.base import BaseCommand
from apps.gis.models import EmergencyService
from apps.core.models import BarangayInfo


class Command(BaseCommand):
    help = "Seed dummy emergency services"

    def handle(self, *args, **kwargs):
        self.stdout.write("Seeding Emergency Services...")

        info = BarangayInfo.objects.first()
        if not info or not info.latitude or not info.longitude:
            self.stdout.write(
                self.style.ERROR(
                    "Barangay coordinates not set. Please complete setup first."
                )
            )
            return

        base_lat = info.latitude
        base_lng = info.longitude

        services = [
            {
                "name": "Barangay Police Outpost",
                "service_type": "police",
                "latitude": base_lat + 0.001,
                "longitude": base_lng + 0.001,
                "contact_number": "911 / (053) 123-4567",
                "address": "Main St, Zone 1",
            },
            {
                "name": "Municipal Fire Station",
                "service_type": "fire",
                "latitude": base_lat - 0.002,
                "longitude": base_lng + 0.003,
                "contact_number": "161 / (053) 987-6543",
                "address": "Public Plaza, Sector 4",
            },
            {
                "name": "District Hospital",
                "service_type": "hospital",
                "latitude": base_lat + 0.003,
                "longitude": base_lng - 0.002,
                "contact_number": "(053) 555-0000",
                "address": "Hospital Road, Zone 2",
            },
            {
                "name": "Community Health Center",
                "service_type": "hospital",
                "latitude": base_lat - 0.001,
                "longitude": base_lng - 0.001,
                "contact_number": "0917-123-4567",
                "address": "Purok 2",
            },
        ]

        for s in services:
            obj, created = EmergencyService.objects.get_or_create(
                name=s["name"], defaults=s
            )
            if created:
                self.stdout.write(self.style.SUCCESS(f"Created: {s['name']}"))
            else:
                self.stdout.write(f"Already exists: {s['name']}")
