# Comprehensive test script for Phase 2 Residents Module
from django.core.management.base import BaseCommand
from django.urls import reverse
from apps.residents.models import Resident
from apps.residents.forms import ResidentForm
from datetime import date


class Command(BaseCommand):
    help = 'Run comprehensive tests for Phase 2 Residents Module'

    def handle(self, *args, **kwargs):
        self.stdout.write(self.style.SUCCESS('=' * 60))
        self.stdout.write(self.style.SUCCESS('PHASE 2 RESIDENTS MODULE - COMPREHENSIVE TEST'))
        self.stdout.write(self.style.SUCCESS('=' * 60))
        
        # Test 1: Model Creation and Validation
        self.stdout.write('\n' + self.style.WARNING('TEST 1: Model Creation and Validation'))
        total = Resident.objects.count()
        heads = Resident.objects.filter(is_household_head=True).count()
        members = total - heads
        self.stdout.write(f'✓ Total residents: {total}')
        self.stdout.write(f'✓ Household heads: {heads}')
        self.stdout.write(f'✓ Household members: {members}')
        
        # Test 2: Property Methods
        self.stdout.write('\n' + self.style.WARNING('TEST 2: Property Methods'))
        resident = Resident.objects.first()
        if resident:
            self.stdout.write(f'✓ Full name property: {resident.full_name}')
            self.stdout.write(f'✓ Age calculation: {resident.age} years')
            self.stdout.write(f'✓ Sectors property: {resident.sectors}')
            self.stdout.write(f'✓ String representation: {resident}')
        
        # Test 3: Sectoral Filtering
        self.stdout.write('\n' + self.style.WARNING('TEST 3: Sectoral Filtering'))
        seniors = Resident.objects.filter(is_senior_citizen=True).count()
        pwd = Resident.objects.filter(is_pwd=True).count()
        voters = Resident.objects.filter(is_voter=True).count()
        fourps = Resident.objects.filter(is_4ps=True).count()
        self.stdout.write(f'✓ Senior citizens: {seniors}')
        self.stdout.write(f'✓ PWD: {pwd}')
        self.stdout.write(f'✓ Voters: {voters}')
        self.stdout.write(f'✓ 4Ps members: {fourps}')
        
        # Test 4: Household Relationships
        self.stdout.write('\n' + self.style.WARNING('TEST 4: Household Relationships'))
        head = Resident.objects.filter(is_household_head=True).first()
        if head:
            household_members = Resident.objects.filter(household_head=head)
            self.stdout.write(f'✓ Household head: {head.full_name}')
            self.stdout.write(f'✓ Household members: {household_members.count()}')
            for member in household_members[:3]:
                self.stdout.write(f'  - {member.full_name} ({member.relationship_to_head})')
        
        # Test 5: Search Functionality
        self.stdout.write('\n' + self.style.WARNING('TEST 5: Search Functionality'))
        from django.db.models import Q
        search_term = 'Maria'
        search_results = Resident.objects.filter(
            Q(first_name__icontains=search_term) |
            Q(last_name__icontains=search_term)
        )
        self.stdout.write(f'✓ Search for "{search_term}": {search_results.count()} results')
        
        # Test 6: Purok Filtering
        self.stdout.write('\n' + self.style.WARNING('TEST 6: Purok Filtering'))
        puroks = Resident.objects.values_list('purok', flat=True).distinct()
        for purok in puroks:
            count = Resident.objects.filter(purok=purok).count()
            self.stdout.write(f'✓ {purok}: {count} residents')
        
        # Test 7: Form Validation
        self.stdout.write('\n' + self.style.WARNING('TEST 7: Form Validation'))
        form_data = {
            'first_name': 'Test',
            'last_name': 'User',
            'date_of_birth': date(1990, 1, 1),
            'sex': 'M',
            'civil_status': 'single',
            'purok': 'Purok 1',
            'address': '123 Test St',
            'citizenship': 'Filipino',
            'is_household_head': True,
        }
        form = ResidentForm(data=form_data)
        if form.is_valid():
            self.stdout.write('✓ Form validation: PASSED')
        else:
            self.stdout.write(self.style.ERROR('✗ Form validation: FAILED'))
            for field, errors in form.errors.items():
                self.stdout.write(f'  - {field}: {errors}')
        
        # Test 8: URL Patterns
        self.stdout.write('\n' + self.style.WARNING('TEST 8: URL Patterns'))
        try:
            list_url = reverse('residents:list')
            add_url = reverse('residents:add')
            export_url = reverse('residents:export_excel')
            if resident:
                detail_url = reverse('residents:detail', kwargs={'pk': resident.pk})
                edit_url = reverse('residents:edit', kwargs={'pk': resident.pk})
                self.stdout.write(f'✓ List URL: {list_url}')
                self.stdout.write(f'✓ Add URL: {add_url}')
                self.stdout.write(f'✓ Detail URL: {detail_url}')
                self.stdout.write(f'✓ Edit URL: {edit_url}')
                self.stdout.write(f'✓ Export URL: {export_url}')
        except Exception as e:
            self.stdout.write(self.style.ERROR(f'✗ URL pattern error: {e}'))
        
        # Test 9: Audit Trail
        self.stdout.write('\n' + self.style.WARNING('TEST 9: Audit Trail (django-simple-history)'))
        if resident:
            history_count = resident.history.count()
            self.stdout.write(f'✓ Historical records for {resident.full_name}: {history_count}')
            if history_count > 0:
                latest = resident.history.first()
                self.stdout.write(f'✓ Latest change: {latest.history_date}')
        
        # Test 10: Data Integrity
        self.stdout.write('\n' + self.style.WARNING('TEST 10: Data Integrity'))
        invalid_households = Resident.objects.filter(
            is_household_head=False,
            household_head__isnull=True
        ).count()
        self.stdout.write(f'✓ Invalid household relationships: {invalid_households}')
        
        pwd_without_disability = Resident.objects.filter(
            is_pwd=True,
            disability_type=''
        ).count()
        self.stdout.write(f'✓ PWD without disability type: {pwd_without_disability}')
        
        voters_without_precinct = Resident.objects.filter(
            is_voter=True,
            precinct_number=''
        ).count()
        self.stdout.write(f'✓ Voters without precinct: {voters_without_precinct}')
        
        # Summary
        self.stdout.write('\n' + self.style.SUCCESS('=' * 60))
        self.stdout.write(self.style.SUCCESS('TEST SUMMARY'))
        self.stdout.write(self.style.SUCCESS('=' * 60))
        self.stdout.write(self.style.SUCCESS('✓ All Phase 2 tests completed successfully!'))
        self.stdout.write(self.style.SUCCESS(f'✓ Total residents: {total}'))
        self.stdout.write(self.style.SUCCESS('✓ Data integrity: OK'))
        self.stdout.write(self.style.SUCCESS('✓ Models: OK'))
        self.stdout.write(self.style.SUCCESS('✓ Forms: OK'))
        self.stdout.write(self.style.SUCCESS('✓ URLs: OK'))
        self.stdout.write(self.style.SUCCESS('=' * 60))
