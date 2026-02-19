import os
import django
import sys
from django.test import Client
from django.urls import reverse

# Setup Django environment
sys.path.append(os.getcwd())
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from apps.core.models import BarangayInfo
from django.contrib.auth import get_user_model

def verify_setup_flow():
    print("--- Verifying Setup Wizard Flow ---")
    
    # 1. Clear existing BarangayInfo for testing
    print("Clearing existing configuration...")
    BarangayInfo.objects.all().delete()
    
    client = Client()
    
    # 2. Test Redirect (Middleware)
    print("Testing Middleware Redirect...")
    response = client.get(reverse('core:login'))
    if response.status_code == 302 and '/setup/' in response.url:
        print("SUCCESS: Redirected to /setup/ when no config exists.")
    else:
        print(f"FAILED: Expected redirect to /setup/, got {response.status_code} - {response.url if hasattr(response, 'url') else ''}")
        return

    # 3. Test Setup Submission
    print("Testing Setup Submission...")
    form_data = {
        'barangay_name': 'Test Barangay',
        'barangay_address': '123 Test St.',
        'barangay_captain': 'Capt. Test',
        'admin_username': 'admin_test',
        'admin_password': 'password123',
        'admin_email': 'admin@test.com',
    }
    
    response = client.post(reverse('core:setup'), form_data)
    
    if response.status_code == 302 and '/login/' in response.url:
        print("SUCCESS: Setup form submitted and redirected to login.")
    else:
        print(f"FAILED: Setup form submission failed. Status: {response.status_code}")
        # print(response.content.decode())
        return

    # 4. Verify Data Persistence
    print("Verifying Data Persistence...")
    if BarangayInfo.objects.exists():
        info = BarangayInfo.objects.first()
        print(f"SUCCESS: BarangayInfo created: {info.name}")
    else:
        print("FAILED: BarangayInfo not created.")
        
    User = get_user_model()
    if User.objects.filter(username='admin_test').exists():
        print("SUCCESS: Admin user created.")
    else:
        print("FAILED: Admin user not created.")

    # 5. Verify Redirect GONE
    print("Verifying Middleware Bypass...")
    response = client.get(reverse('core:login'))
    if response.status_code == 200:
        print("SUCCESS: Access to login allowed after setup.")
    else:
        print(f"FAILED: Still redirecting? Status: {response.status_code}")

if __name__ == '__main__':
    verify_setup_flow()
