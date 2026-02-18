from django.core.management.base import BaseCommand
from apps.residents.models import Resident
from apps.gis.views import ResidentGeoJSONView
from django.test import RequestFactory
from django.urls import reverse
from django.contrib.auth import get_user_model
import json

class Command(BaseCommand):
    help = 'Verify GIS Implementation'

    def handle(self, *args, **kwargs):
        self.stdout.write("Verifying GIS Implementation...")
        
        # 1. Check if residents exist with coordinates
        residents_with_coords = Resident.objects.filter(latitude__isnull=False, longitude__isnull=False).count()
        self.stdout.write(f"Residents with coordinates: {residents_with_coords}")
        
        if residents_with_coords == 0:
            self.stdout.write(self.style.WARNING("WARNING: No residents have coordinates. Map will be empty."))
            self.stdout.write("Adding dummy data for testing...")
            try:
                # Try to get an existing resident or create a dummy one
                resident = Resident.objects.first()
                if not resident:
                    resident = Resident.objects.create(
                        first_name="Test", last_name="Resident", 
                        date_of_birth="2000-01-01", sex="M", civil_status="single",
                        purok="Purok 1", address="Test Address"
                    )
                    self.stdout.write("Created dummy resident.")
                    
                resident.latitude = 14.5995
                resident.longitude = 120.9842
                resident.save()
                self.stdout.write(self.style.SUCCESS(f"Added coordinates to resident: {resident}"))
            except Exception as e:
                self.stdout.write(self.style.ERROR(f"Error adding dummy data: {e}"))

        # 2. Test the View
        factory = RequestFactory()
        # We can't reverse easily without full URL conf loaded in some contexts, but let's try
        try:
            url = reverse('gis:resident_geojson')
        except:
            url = '/gis/api/residents/'
            
        request = factory.get(url)
        
        User = get_user_model()
        user = User.objects.first()
        if not user:
            user = User.objects.create_superuser('admin', 'admin@example.com', 'password')
            self.stdout.write("Created superuser 'admin'")
            
        request.user = user
        
        view = ResidentGeoJSONView.as_view()
        response = view(request)
        
        if response.status_code == 200:
            self.stdout.write("API Endpoint returned 200 OK")
            content = json.loads(response.content)
            self.stdout.write(f"GeoJSON Type: {content.get('type')}")
            self.stdout.write(f"Number of Features: {len(content.get('features'))}")
            
            if len(content.get('features')) > 0:
                self.stdout.write(self.style.SUCCESS("SUCCESS: Data is being returned correctly."))
            else:
                self.stdout.write(self.style.WARNING("WARNING: GeoJSON is empty (but valid)."))
        else:
            self.stdout.write(self.style.ERROR(f"FAILED: API returned {response.status_code}"))
