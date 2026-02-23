from django.core.management.base import BaseCommand
from django.utils import timezone
from django.contrib.auth import get_user_model
from apps.residents.models import Resident
from apps.blotter.models import BlotterCase, Complainant, Respondent, Hearing
from apps.certificates.models import Certificate, CertificateType
from apps.finance.models import Fee, OfficialReceipt
from apps.business.models import BusinessPermit
from datetime import date, timedelta
import random

User = get_user_model()

class Command(BaseCommand):
    help = 'Evaluate system functions, forms, and logic'

    def handle(self, *args, **kwargs):
        self.stdout.write(self.style.SUCCESS('Starting System Evaluation...'))
        
        # 0. Setup Prerequisites (User, Resident)
        self.evaluate_prerequisites()
        
        # 1. Blotter Module
        self.evaluate_blotter()
        
        # 2. Finance Module
        self.evaluate_finance()
        
        # 3. Certificates Module
        self.evaluate_certificates()
        
        # 4. Business Module
        self.evaluate_business()
        
        self.stdout.write(self.style.SUCCESS('\nSystem Evaluation Completed Successfully!'))

    def evaluate_prerequisites(self):
        self.stdout.write('\n[0] Checking Prerequisites...')
        
        # Ensure Admin User
        user, created = User.objects.get_or_create(username='eval_admin', defaults={'email': 'admin@eval.local', 'role': 'admin'})
        if created:
            user.set_password('admin123')
            user.save()
            self.stdout.write(' - Created eval_admin user')
        else:
            self.stdout.write(' - Found existing eval_admin user')
        self.user = user

        # Ensure Resident
        resident, created = Resident.objects.get_or_create(
            first_name='Eval',
            last_name='Resident',
            defaults={
                'middle_name': 'Test',
                'date_of_birth': date(1990, 1, 1),
                'sex': 'M',
                'civil_status': 'single',
                'citizenship': 'Filipino',
                'purok': 'Purok 1',
                'address': 'Eval Address',
                'is_household_head': True
            }
        )
        self.resident = resident
        self.stdout.write(f' - Using resident: {resident}')

    def evaluate_blotter(self):
        self.stdout.write('\n[1] Evaluating Blotter Module...')
        
        # Create Case
        case = BlotterCase.objects.create(
            incident_type='theft',
            incident_date=timezone.now(),
            incident_location='Purok 1',
            narrative='Test narrative for evaluation',
            created_by=self.user
        )
        self.stdout.write(f' - Created Case: {case.case_number}')
        
        # Add Complainant/Respondent
        Complainant.objects.create(case=case, resident=self.resident)
        Respondent.objects.create(case=case, name='John Doe (Non-resident)', contact_number='09123456789')
        self.stdout.write(' - Added participants')
        
        # Schedule Hearing
        hearing = Hearing.objects.create(
            case=case,
            scheduled_at=timezone.now() + timedelta(days=3),
            status='scheduled'
        )
        self.stdout.write(f' - Scheduled Hearing: {hearing.scheduled_at}')
        
        # Verify Logic: Next Hearing
        if case.next_hearing == hearing:
             self.stdout.write(self.style.SUCCESS(' - Logic Check Passed: next_hearing property works'))
        else:
             self.stdout.write(self.style.ERROR(' - Logic Check Failed: next_hearing property mismatch'))

    def evaluate_finance(self):
        self.stdout.write('\n[2] Evaluating Finance Module...')
        
        # Create Fee
        fee, _ = Fee.objects.get_or_create(name='Test Fee', defaults={'default_amount': 50.00})
        self.stdout.write(f' - Fee Configured: {fee.name}')
        
        # Create Receipt
        or_num = f'OR-{random.randint(10000,99999)}'
        receipt = OfficialReceipt.objects.create(
            or_number=or_num,
            payor=self.resident.full_name,
            particulars='Payment for Cert',
            amount=50.00,
            created_by=self.user
        )
        self.stdout.write(f' - OR Generated: {receipt.or_number}')
        self.last_receipt = receipt

    def evaluate_certificates(self):
        self.stdout.write('\n[3] Evaluating Certificates Module...')
        
        # Create Type
        type_obj, _ = CertificateType.objects.get_or_create(
            name='Barangay Clearance',
            slug='brgy-clearance',
            defaults={'default_price': 50.00, 'template_file': 'certs/clearance.html'}
        )
        
        # Issue Certificate
        cert = Certificate.objects.create(
            resident=self.resident,
            certificate_type=type_obj,
            purpose='Employment',
            or_number=self.last_receipt.or_number,
            amount_paid=50.00,
            status='paid',
            issued_by=self.user,
            issued_at=timezone.now()
        )
        self.stdout.write(f' - Certificate Issued: {cert.transaction_number}')
        
        if cert.transaction_number.startswith('CERT-'):
            self.stdout.write(self.style.SUCCESS(' - Logic Check Passed: Transaction ID generation'))
        else:
            self.stdout.write(self.style.ERROR(' - Logic Check Failed: Transaction ID generation'))

    def evaluate_business(self):
        self.stdout.write('\n[4] Evaluating Business Module...')
        
        # Issue Permit
        permit = BusinessPermit.objects.create(
            business_name='Eval Corp',
            owner_name='Eval Owner',
            address='Eval St.',
            nature_of_business='Software',
            expiration_date=date(2026, 12, 31),
            status='active',
            created_by=self.user
        )
        self.stdout.write(f' - Permit Issued: {permit.permit_number}')
        
        # Configurable expiry check
        if not permit.is_expired:
             self.stdout.write(self.style.SUCCESS(' - Logic Check Passed: Expiry logic correct'))
        else:
             self.stdout.write(self.style.ERROR(' - Logic Check Failed: Permit marked expired prematurely'))
