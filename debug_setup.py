from django.conf import settings
from django.urls import reverse
from apps.core.models import BarangayInfo

print("--- DIAGNOSTICS START ---")
print(f"Middleware order:")
for i, mw in enumerate(settings.MIDDLEWARE):
    if 'setup' in mw or 'license' in mw or 'auth' in mw:
        print(f"{i}: {mw}")

print(f"Resolution setup: {reverse('core:setup')}")
print(f"Resolution login: {reverse('core:login')}")

count = BarangayInfo.objects.count()
print(f"BarangayInfo count: {count}")

print("--- DIAGNOSTICS END ---")
