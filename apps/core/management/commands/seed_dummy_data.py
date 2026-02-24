"""
Management command: seed_dummy_data
Populates the database with realistic Philippine barangay data for development/demo purposes.
Safe to re-run — uses update_or_create / get_or_create wherever possible.
"""
from django.core.management.base import BaseCommand
from django.utils import timezone
from datetime import date, timedelta


class Command(BaseCommand):
    help = 'Seeds the database with dummy officials, residents, business permits, and blotter cases.'

    def handle(self, *args, **kwargs):
        self.stdout.write(self.style.MIGRATE_HEADING('\n=== Seeding Dummy Data ===\n'))
        self._seed_officials()
        residents = self._seed_residents()
        self._seed_business_permits()
        self._seed_blotter_cases(residents)
        self.stdout.write(self.style.SUCCESS('\n✓ Done. All dummy data seeded successfully.\n'))

    # ── Officials ──────────────────────────────────────────────────────────

    def _seed_officials(self):
        from apps.core.models import BarangayOfficial, BarangayInfo

        roster = [
            # (order, position, committee, honorific, first, middle, last, suffix, term_start, term_end, contact)
            (0, 'punong_barangay', '',               'Hon.', 'Ricardo',  'Santos',  'Dela Cruz',  'Jr.',  '2023-01-01', '2026-12-31', '09171234567'),
            (1, 'kagawad',        'peace_order',     'Hon.', 'Maria',    'Reyes',   'Santos',     '',     '2023-01-01', '2026-12-31', '09181234568'),
            (2, 'kagawad',        'health',          'Hon.', 'Jose',     'Cruz',    'Garcia',     '',     '2023-01-01', '2026-12-31', '09191234569'),
            (3, 'kagawad',        'education',       'Hon.', 'Ana',      'Ramos',   'Villanueva', '',     '2023-01-01', '2026-12-31', '09201234570'),
            (4, 'kagawad',        'infrastructure',  'Hon.', 'Pedro',    'Lim',     'Reyes',      '',     '2023-01-01', '2026-12-31', '09211234571'),
            (5, 'kagawad',        'livelihood',      'Hon.', 'Elena',    'Torres',  'Mendoza',    '',     '2023-01-01', '2026-12-31', '09221234572'),
            (6, 'kagawad',        'environment',     'Hon.', 'Carlos',   'Bautista','Lopez',      '',     '2023-01-01', '2026-12-31', '09231234573'),
            (7, 'kagawad',        'women',           'Hon.', 'Rosario',  'Aquino',  'Fernandez',  '',     '2023-01-01', '2026-12-31', '09241234574'),
            (8, 'sk_chairman',    'youth',           'Hon.', 'Kevin',    'Diaz',    'Castillo',   '',     '2023-01-01', '2025-12-31', '09251234575'),
            (9, 'secretary',      '',                '',     'Lourdes',  'Marquez', 'Ramos',      '',     '2023-01-01', '2026-12-31', '09261234576'),
            (10,'treasurer',      'finance',         '',     'Ferdinand','Ocampo',  'Pascual',    '',     '2023-01-01', '2026-12-31', '09271234577'),
        ]

        captain_name = ''
        for row in roster:
            order, position, committee, honorific, first, middle, last, suffix, ts, te, contact = row
            official, created = BarangayOfficial.objects.get_or_create(
                first_name=first, last_name=last, position=position,
                defaults={
                    'order': order,
                    'committee': committee,
                    'honorific': honorific,
                    'middle_name': middle,
                    'suffix': suffix,
                    'term_start': date.fromisoformat(ts),
                    'term_end': date.fromisoformat(te),
                    'contact_number': contact,
                    'is_active': True,
                }
            )
            action = 'Created' if created else 'Already exists'
            self.stdout.write(f'  [{action}] {official}')
            if position == 'punong_barangay':
                captain_name = official.display_name.upper()

        # Sync captain name to BarangayInfo
        if captain_name:
            info = BarangayInfo.objects.first()
            if info:
                info.captain_name = captain_name
                info.save(update_fields=['captain_name'])
                self.stdout.write(f'  [Synced] captain_name → {captain_name}')

        self.stdout.write(self.style.SUCCESS(f'  → {len(roster)} officials processed.\n'))

    # ── Residents ─────────────────────────────────────────────────────────

    def _seed_residents(self):
        from apps.residents.models import Resident, Purok
        from django.utils.text import slugify

        residents_data = [
            # (first, middle, last, suffix, dob, sex, civil_status, purok, address, employment, occupation, mobile, sectors)
            ('Juan',      'Santos',   'Dela Cruz',  '',    '1985-03-15', 'M', 'married',   'Purok 1', '123 Mabini St.',     'employed',      'Farmer',          '09301234580', {}),
            ('Maria',     'Reyes',    'Santos',     '',    '1990-07-22', 'F', 'single',    'Purok 2', '45 Rizal Ave.',      'employed',      'Teacher',         '09311234581', {}),
            ('Roberto',   'Cruz',     'Garcia',     '',    '1975-11-08', 'M', 'married',   'Purok 1', '78 Bonifacio St.',   'self_employed', 'Sari-Sari Store', '09321234582', {}),
            ('Lita',      'Bautista', 'Villanueva', '',    '1968-05-30', 'F', 'widowed',   'Purok 3', '12 Aguinaldo Rd.',   'unemployed',    '',                '09331234583', {'is_senior_citizen': True}),
            ('Pedro',     'Lim',      'Reyes',      '',    '1995-09-14', 'M', 'single',    'Purok 2', '34 MacArthur Blvd.', 'student',       '',                '09341234584', {}),
            ('Corazon',   'Torres',   'Mendoza',    '',    '1982-01-25', 'F', 'married',   'Purok 4', '56 Quezon St.',      'employed',      'Nurse',           '09351234585', {}),
            ('Antonio',   'Ocampo',   'Lopez',      'Sr.', '1955-12-03', 'M', 'married',   'Purok 1', '89 Magsaysay Ave.',  'retired',       '',                '09361234586', {'is_senior_citizen': True, 'is_voter': True}),
            ('Cristina',  'Aquino',   'Fernandez',  '',    '2002-06-18', 'F', 'single',    'Purok 3', '23 Luna St.',        'student',       '',                '09371234587', {}),
            ('Rodrigo',   'Diaz',     'Castillo',   '',    '1978-04-07', 'M', 'separated', 'Purok 2', '67 Legaspi Rd.',     'self_employed', 'Tricycle Driver', '09381234588', {'is_voter': True}),
            ('Natividad', 'Marquez',  'Ramos',      '',    '1970-08-19', 'F', 'married',   'Purok 4', '101 Mabini St.',     'employed',      'Barangay Worker', '09391234589', {'is_voter': True, 'is_4ps': True}),
            ('Eduardo',   'Pascual',  'Gutierrez',  '',    '1988-02-28', 'M', 'married',   'Purok 3', '15 Roxas Blvd.',     'employed',      'Security Guard',  '09401234590', {}),
            ('Josefina',  'Castro',   'Navarro',    '',    '1960-10-11', 'F', 'widowed',   'Purok 4', '28 Quezon Ave.',     'unemployed',    '',                '09411234591', {'is_senior_citizen': True, 'is_indigent': True}),
        ]

        # Ensure Puroks exist
        purok_names = set(row[7] for row in residents_data)
        purok_map = {}
        for p_name in purok_names:
            p_obj, _ = Purok.objects.get_or_create(
                name=p_name,
                defaults={'slug': slugify(p_name)}
            )
            purok_map[p_name] = p_obj

        created_residents = []
        for row in residents_data:
            first, middle, last, suffix, dob, sex, civil, purok_name, address, emp, occ, mobile, sectors = row
            purok_obj = purok_map.get(purok_name)
            
            defaults = {
                'middle_name': middle,
                'suffix': suffix,
                'date_of_birth': date.fromisoformat(dob),
                'sex': sex,
                'civil_status': civil,
                'purok': purok_name,
                'purok_link': purok_obj,
                'address': address,
                'employment_status': emp,
                'occupation': occ,
                'mobile_number': mobile,
                'citizenship': 'Filipino',
                'is_active': True,
                **sectors,
            }
            resident, created = Resident.objects.get_or_create(
                first_name=first, last_name=last,
                defaults=defaults
            )
            action = 'Created' if created else 'Already exists'
            self.stdout.write(f'  [{action}] {resident.full_name}')
            created_residents.append(resident)

        self.stdout.write(self.style.SUCCESS(f'  → {len(residents_data)} residents processed.\n'))
        return created_residents

    # ── Business Permits ──────────────────────────────────────────────────

    def _seed_business_permits(self):
        from apps.business.models import BusinessPermit
        from django.contrib.auth import get_user_model
        User = get_user_model()
        admin = User.objects.filter(is_superuser=True).first()

        businesses = [
            # (name, owner, address, nature, gross_sales, fee, or_num, status)
            ('Santos Sari-Sari Store',        'Juan Santos Dela Cruz',   'Purok 1, 123 Mabini St.',     'Retail - Sari-Sari Store',          250000.00, 500.00,  'OR-2026-001', 'active'),
            ('Garcia General Trading',        'Roberto Cruz Garcia',     'Purok 1, 78 Bonifacio St.',   'General Merchandise',               750000.00, 1200.00, 'OR-2026-002', 'active'),
            ('Mendoza Lechon Manok',          'Corazon Torres Mendoza',  'Purok 4, 56 Quezon St.',      'Food - Lechon Manok',               180000.00, 350.00,  'OR-2026-003', 'active'),
            ('Castillo Transport Services',   'Rodrigo Diaz Castillo',   'Purok 2, 67 Legaspi Rd.',    'Transport - Tricycle for Hire',     120000.00, 250.00,  'OR-2026-004', 'pending'),
            ('Navarro Beauty Salon',          'Josefina Castro Navarro', 'Purok 4, 28 Quezon Ave.',    'Personal Services - Beauty Salon',   90000.00, 200.00,  'OR-2026-005', 'active'),
        ]

        today = date.today()
        for row in businesses:
            name, owner, address, nature, gross, fee, orno, status = row
            permit, created = BusinessPermit.objects.get_or_create(
                business_name=name,
                defaults={
                    'owner_name': owner,
                    'owner_address': address,
                    'address': address,
                    'nature_of_business': nature,
                    'gross_sales': gross,
                    'clearance_fee': fee,
                    'or_number': orno,
                    'status': status,
                    'issued_date': today,
                    'expiration_date': date(today.year, 12, 31),
                    'created_by': admin,
                }
            )
            action = 'Created' if created else 'Already exists'
            self.stdout.write(f'  [{action}] {permit.business_name} ({permit.permit_number})')

        self.stdout.write(self.style.SUCCESS(f'  → {len(businesses)} business permits processed.\n'))

    # ── Blotter Cases ─────────────────────────────────────────────────────

    def _seed_blotter_cases(self, residents):
        from apps.blotter.models import BlotterCase, Complainant, Respondent, Hearing
        from django.contrib.auth import get_user_model
        User = get_user_model()
        admin = User.objects.filter(is_superuser=True).first()

        now = timezone.now()

        cases_data = [
            {
                'incident_type': 'physical_injury',
                'incident_date': now - timedelta(days=30),
                'incident_location': 'Purok 1, near the basketball court',
                'narrative': (
                    'Complainant reported that respondent allegedly punched him during a basketball game '
                    'on the afternoon of the incident, causing bruising on his left cheek. '
                    'Witnesses present at the time confirmed the altercation.'
                ),
                'status': 'mediation',
                'complainant_idx': 0,
                'respondent_idx': 2,
                'hearings': [
                    (now + timedelta(days=5), 'scheduled'),
                ],
            },
            {
                'incident_type': 'debt_collection',
                'incident_date': now - timedelta(days=45),
                'incident_location': 'Purok 2, Santos Sari-Sari Store',
                'narrative': (
                    'Complainant claims respondent borrowed ₱5,000 from her store on credit '
                    'six months ago and has failed to pay despite repeated demands. '
                    'A promissory note signed by the respondent was presented as evidence.'
                ),
                'status': 'conciliation',
                'complainant_idx': 0,
                'respondent_idx': 4,
                'hearings': [
                    (now - timedelta(days=20), 'completed'),
                    (now + timedelta(days=10), 'scheduled'),
                ],
            },
            {
                'incident_type': 'slander',
                'incident_date': now - timedelta(days=15),
                'incident_location': 'Purok 3, in front of the community center',
                'narrative': (
                    'Complainant alleges that respondent publicly made false and defamatory statements '
                    'about her reputation in front of several neighbors on the date of the incident. '
                    'Multiple witnesses have been identified who heard the statements.'
                ),
                'status': 'mediation',
                'complainant_idx': 5,
                'respondent_idx': 9,
                'hearings': [
                    (now + timedelta(days=3), 'scheduled'),
                ],
            },
            {
                'incident_type': 'boundary_dispute',
                'incident_date': now - timedelta(days=60),
                'incident_location': 'Between Lots 12 and 13, Purok 4',
                'narrative': (
                    'Both parties claim ownership of a 2-meter strip of land between their properties. '
                    'Respondent allegedly erected a fence encroaching on the complainant\'s land. '
                    'Tax declarations and old survey maps were submitted by both parties.'
                ),
                'status': 'settled',
                'settlement_details': (
                    'Both parties agreed to have the disputed land surveyed by a licensed geodetic engineer '
                    'within 30 days. Costs shall be shared equally. The fence shall remain in place '
                    'until the survey is completed.'
                ),
                'complainant_idx': 6,
                'respondent_idx': 11,
                'hearings': [
                    (now - timedelta(days=40), 'completed'),
                    (now - timedelta(days=20), 'completed'),
                ],
            },
            {
                'incident_type': 'threats',
                'incident_date': now - timedelta(days=7),
                'incident_location': 'Purok 2, along Rizal Avenue',
                'narrative': (
                    'Complainant reported that the respondent verbally threatened her life after a heated '
                    'argument over a parking dispute. The complainant is fearful for her safety. '
                    'No physical harm occurred but the threats were witnessed by two bystanders.'
                ),
                'status': 'cfa',
                'complainant_idx': 1,
                'respondent_idx': 8,
                'hearings': [
                    (now - timedelta(days=5), 'completed'),
                ],
            },
        ]

        for case_data in cases_data:
            c_idx = case_data.pop('complainant_idx')
            r_idx = case_data.pop('respondent_idx')
            hearings_data = case_data.pop('hearings')
            settlement = case_data.pop('settlement_details', '')

            # Check if equivalent case already exists (by incident_type + incident_date)
            existing = BlotterCase.objects.filter(
                incident_type=case_data['incident_type'],
                incident_date__date=case_data['incident_date'].date()
            ).first()

            if existing:
                self.stdout.write(f'  [Already exists] {existing.case_number}')
                continue

            case = BlotterCase.objects.create(
                **case_data,
                settlement_details=settlement,
                created_by=admin,
            )

            # Complainant
            complainant_resident = residents[c_idx] if c_idx < len(residents) else None
            Complainant.objects.create(case=case, resident=complainant_resident)

            # Respondent
            respondent_resident = residents[r_idx] if r_idx < len(residents) else None
            Respondent.objects.create(case=case, resident=respondent_resident)

            # Hearings
            for sched_at, status in hearings_data:
                Hearing.objects.create(case=case, scheduled_at=sched_at, status=status)

            self.stdout.write(f'  [Created] {case.case_number} — {case.get_incident_type_display()} ({case.get_status_display()})')

        self.stdout.write(self.style.SUCCESS(f'  → {len(cases_data)} blotter cases processed.\n'))
