import requests
from django.core.management.base import BaseCommand
from apps.gis.models import EmergencyService
from apps.core.models import BarangayInfo


class Command(BaseCommand):
    help = "Imports nearby emergency services (police, fire, hospitals) from OpenStreetMap via Overpass API"

    def add_arguments(self, parser):
        parser.add_argument(
            "--radius",
            type=int,
            default=5000,
            help="Radius in meters for the search (default: 5000)",
        )
        parser.add_argument(
            "--dry-run",
            action="store_true",
            help="Perform a dry run without saving to the database",
        )

    def handle(self, *args, **options):
        radius = options["radius"]
        dry_run = options["dry_run"]

        info = BarangayInfo.objects.first()
        if not info or not info.latitude or not info.longitude:
            self.stdout.write(
                self.style.ERROR(
                    "Error: Barangay coordinates are not set. Please configure them in Setup."
                )
            )
            return

        lat = info.latitude
        lng = info.longitude

        self.stdout.write(
            f"Searching for emergency services within {radius}m of {lat}, {lng}..."
        )

        # Overpass API query
        # amenity=police, amenity=fire_station, amenity=hospital
        query = f"""
        [out:json][timeout:25];
        (
          node["amenity"~"police|fire_station|hospital"](around:{radius},{lat},{lng});
          way["amenity"~"police|fire_station|hospital"](around:{radius},{lat},{lng});
          relation["amenity"~"police|fire_station|hospital"](around:{radius},{lat},{lng});
        );
        out center;
        """

        url = "https://overpass-api.de/api/interpreter"
        try:
            # Set a 30s timeout to prevent hanging on slow external API response
            response = requests.post(url, data={"data": query}, timeout=30)
            response.raise_for_status()
            data = response.json()
        except requests.exceptions.Timeout:
            self.stdout.write(
                self.style.ERROR(
                    "API Error: Request timed out after 30 seconds. Overpass API might be busy."
                )
            )
            return
        except Exception as e:
            self.stdout.write(self.style.ERROR(f"API Error: {str(e)}"))
            return

        elements = data.get("elements", [])
        if not elements:
            self.stdout.write(self.style.WARNING("No services found in this area."))
            return

        self.stdout.write(f"Found {len(elements)} potential services. Processing...")

        created_count = 0
        updated_count = 0
        skipped_count = 0

        type_map = {
            "police": "police",
            "fire_station": "fire",
            "hospital": "hospital",
            "clinic": "hospital",
            "doctors": "hospital",
        }

        for el in elements:
            tags = el.get("tags", {})
            osm_id = el.get("id")

            # Extract coordinates (Overpass 'center' or 'lat/lon')
            plat = el.get("lat") or el.get("center", {}).get("lat")
            plng = el.get("lon") or el.get("center", {}).get("lon")

            if not plat or not plng:
                continue

            name = (
                tags.get("name")
                or tags.get("operator")
                or f"Unknown {tags.get('amenity')}"
            )
            osm_type = tags.get("amenity")
            service_type = type_map.get(
                osm_type, "police"
            )  # Fallback to police if unknown

            # Simple address construction
            address = (
                tags.get("addr:full")
                or f"{tags.get('addr:street', '')} {tags.get('addr:city', '')}".strip()
            )
            contact = tags.get("phone") or tags.get("contact:phone") or ""

            if dry_run:
                self.stdout.write(
                    f"[Dry Run] Found: {name} ({service_type}) at {plat}, {plng}"
                )
                continue

            # Update or Create
            service, created = EmergencyService.objects.update_or_create(
                osm_id=osm_id,
                defaults={
                    "name": name,
                    "service_type": service_type,
                    "latitude": plat,
                    "longitude": plng,
                    "address": address,
                    "contact_number": contact,
                    "is_active": True,
                },
            )

            if created:
                created_count += 1
                self.stdout.write(self.style.SUCCESS(f"  [Created] {name}"))
            else:
                updated_count += 1
                self.stdout.write(f"  [Updated] {name}")

        if not dry_run:
            self.stdout.write(
                self.style.SUCCESS(
                    f"\nCompleted: {created_count} created, {updated_count} updated, {skipped_count} skipped."
                )
            )
        else:
            self.stdout.write(
                self.style.SUCCESS("\nDry run completed. No data was saved.")
            )
