import os
import django
import sys
import json

# Setup Django environment
sys.path.append(os.getcwd())
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from django.test import RequestFactory
from django.urls import reverse
from apps.gis.views import ResidentGeoJSONView
from apps.residents.models import Resident

def verify_gis():
    print("Verifying GIS Implementation...")
    
    # 1. Check if residents exist with coordinates
    residents_with_coords = Resident.objects.filter(latitude__isnull=False, longitude__isnull=False).count()
    print(f"Residents with coordinates: {residents_with_coords}")
    
    if residents_with_coords == 0:
        print("WARNING: No residents have coordinates. Map will be empty.")
        print("Adding dummy data for testing...")
        try:
            # Try to get an existing resident or create a dummy one
            resident = Resident.objects.first()
            if not resident:
                resident = Resident.objects.create(
                    first_name="Test", last_name="Resident", 
                    date_of_birth="2000-01-01", sex="M", civil_status="single",
                    purok="Purok 1", address="Test Address"
                )
                print("Created dummy resident.")
                
            resident.latitude = 14.5995
            resident.longitude = 120.9842
            resident.save()
            print(f"Added coordinates to resident: {resident}")
        except Exception as e:
            print(f"Error adding dummy data: {e}")

    # 2. Test the View
    factory = RequestFactory()
    request = factory.get(reverse('gis:resident_geojson'))
    request.user = None # We need to mock a user if LoginRequiredMixin is used, but RequestFactory doesn't do middleware.
    
    # Actually, because of LoginRequiredMixin, we can't easily test with RequestFactory without a user.
    # Let's just check the logic directly or mock the request user.
    from django.contrib.auth.models import User
    user = User.objects.first()
    if not user:
        user = User.objects.create_superuser('admin', 'admin@example.com', 'password')
        print("Created superuser 'admin'")
        
    request.user = user
    
    view = ResidentGeoJSONView.as_view()
    response = view(request)
    
    if response.status_code == 200:
        print("API Endpoint returned 200 OK")
        content = json.loads(response.content)
        print(f"GeoJSON Type: {content.get('type')}")
        print(f"Number of Features: {len(content.get('features'))}")
        
        if len(content.get('features')) > 0:
            print("SUCCESS: Data is being returned correctly.")
        else:
            print("WARNING: GeoJSON is empty (but valid).")
    else:
        print(f"FAILED: API returned {response.status_code}")

if __name__ == '__main__':
    verify_gis()
