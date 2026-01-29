import os
import django
from django.utils import timezone
from datetime import timedelta

# Set up Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings.dev')
django.setup()

from apps.blotter.models import BlotterCase, Complainant, Respondent, Hearing
from apps.residents.models import Resident
from django.contrib.auth import get_user_model

User = get_user_model()

def seed_blotter():
    print("Seeding Blotter Data...")
    
    admin_user = User.objects.filter(is_superuser=True).first()
    if not admin_user:
        print("No admin user found. Please create one first.")
        return

    # Clear existing data
    BlotterCase.objects.all().delete()
    
    residents = Resident.objects.all()
    if residents.count() < 3:
        print("Not enough residents to seed blotter. Please seed residents first.")
        return

    # Case 1: Settlement reached
    case1 = BlotterCase.objects.create(
        incident_type='boundary_dispute',
        incident_date=timezone.now() - timedelta(days=5),
        incident_location='Purok 1, near the elementary school',
        narrative='Dispute over the placement of a concrete fence. Both parties claim ownership of the 2-meter strip of land.',
        status='settled',
        created_by=admin_user
    )
    Complainant.objects.create(case=case1, resident=residents[0])
    Respondent.objects.create(case=case1, resident=residents[1])
    Hearing.objects.create(
        case=case1, 
        scheduled_at=timezone.now() - timedelta(days=2), 
        status='completed',
        remarks='Agreement reached. Both parties agreed to re-survey the land.'
    )

    # Case 2: Ongoing Mediation
    case2 = BlotterCase.objects.create(
        incident_type='theft',
        incident_date=timezone.now() - timedelta(days=2),
        incident_location='Purok 3, Public Market',
        narrative='Missing mobile phone (iPhone 13) allegedly taken from the complainant\'s table while they were eating.',
        status='mediation',
        created_by=admin_user
    )
    Complainant.objects.create(case=case2, resident=residents[2])
    Respondent.objects.create(case=case2, name="Unknown Respondent", address="Purok 4")
    Hearing.objects.create(
        case=case2, 
        scheduled_at=timezone.now() + timedelta(days=1, hours=2), 
        status='scheduled'
    )

    # Case 3: Slander (Criminal)
    case3 = BlotterCase.objects.create(
        incident_type='slander',
        incident_date=timezone.now() - timedelta(days=1),
        incident_location='Purok 2, Street Corner',
        narrative='The respondent allegedly shouted defamatory words at the complainant in public, causing embarrassment.',
        status='conciliation',
        created_by=admin_user
    )
    Complainant.objects.create(case=case3, name="Marites Chismosa", address="Purok 2", contact_number="09171234567")
    Respondent.objects.create(case=case3, resident=residents[1])
    Hearing.objects.create(
        case=case3, 
        scheduled_at=timezone.now() + timedelta(hours=3), 
        status='scheduled'
    )

    print(f"Successfully seeded {BlotterCase.objects.count()} cases!")

if __name__ == '__main__':
    seed_blotter()
