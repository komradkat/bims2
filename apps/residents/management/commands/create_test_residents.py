# Test script for Phase 2 Residents Module
from django.core.management.base import BaseCommand
from apps.residents.models import Resident
from datetime import date, timedelta
import random


class Command(BaseCommand):
    help = "Create test data for residents module"

    def add_arguments(self, parser):
        parser.add_argument(
            "--count", type=int, default=5, help="Number of household heads to create"
        )

    def handle(self, *args, **kwargs):
        count = kwargs["count"]
        self.stdout.write(
            self.style.SUCCESS(f"Creating {count} household heads and their members...")
        )

        # Sample data
        first_names = [
            "Juan",
            "Maria",
            "Jose",
            "Ana",
            "Pedro",
            "Rosa",
            "Carlos",
            "Elena",
            "Miguel",
            "Sofia",
        ]
        middle_names = [
            "Santos",
            "Cruz",
            "Reyes",
            "Garcia",
            "Lopez",
            "Ramos",
            "Torres",
            "Flores",
        ]
        last_names = [
            "Dela Cruz",
            "Santos",
            "Reyes",
            "Garcia",
            "Lopez",
            "Martinez",
            "Hernandez",
            "Gonzales",
        ]
        puroks = ["Purok 1", "Purok 2", "Purok 3", "Sitio Kawayan"]

        # Create household heads
        household_heads = []
        for i in range(count):
            age = random.randint(35, 65)
            dob = date.today() - timedelta(days=age * 365)

            resident = Resident.objects.create(
                first_name=random.choice(first_names),
                middle_name=random.choice(middle_names),
                last_name=random.choice(last_names),
                date_of_birth=dob,
                sex=random.choice(["M", "F"]),
                civil_status=random.choice(["married", "single", "widowed"]),
                citizenship="Filipino",
                purok=random.choice(puroks),
                address=f"{random.randint(1, 100)} {random.choice(['Main St', 'Oak Ave', 'Pine Rd', 'Maple Dr'])}",
                years_of_residency=random.randint(5, 30),
                is_household_head=True,
                mobile_number=f"0917{random.randint(1000000, 9999999)}",
                is_senior_citizen=(age >= 60),
                is_voter=True,
                precinct_number=f"{random.randint(1, 999):03d}A",
                occupation=random.choice(
                    ["Farmer", "Driver", "Teacher", "Vendor", "Carpenter"]
                ),
                educational_attainment=random.choice(
                    ["high_school_graduate", "college_level", "elementary_graduate"]
                ),
                employment_status=random.choice(["employed", "self_employed"]),
            )
            household_heads.append(resident)
            self.stdout.write(f"Created household head: {resident.full_name}")

        # Create household members
        for head in household_heads:
            num_members = random.randint(2, 5)
            for j in range(num_members):
                age = random.randint(5, 40)
                dob = date.today() - timedelta(days=age * 365)

                member = Resident.objects.create(
                    first_name=random.choice(first_names),
                    middle_name=random.choice(middle_names),
                    last_name=head.last_name,  # Same last name as head
                    date_of_birth=dob,
                    sex=random.choice(["M", "F"]),
                    civil_status="single"
                    if age < 18
                    else random.choice(["single", "married"]),
                    citizenship="Filipino",
                    purok=head.purok,  # Same purok as head
                    address=head.address,  # Same address as head
                    years_of_residency=head.years_of_residency,
                    is_household_head=False,
                    household_head=head,
                    relationship_to_head=random.choice(
                        ["Spouse", "Son", "Daughter", "Parent"]
                    ),
                    mobile_number=f"0917{random.randint(1000000, 9999999)}"
                    if age >= 18
                    else "",
                    is_pwd=random.choice([True, False])
                    if random.random() < 0.1
                    else False,
                    disability_type="Visual Impairment"
                    if random.random() < 0.5
                    else "Orthopedic",
                    is_4ps=random.choice([True, False])
                    if random.random() < 0.2
                    else False,
                    occupation=random.choice(["Student", "None", "Helper"])
                    if age < 18
                    else random.choice(["Farmer", "Driver", "Vendor"]),
                    educational_attainment="elementary_level"
                    if age < 12
                    else random.choice(["high_school_level", "college_level"]),
                    employment_status="student"
                    if age < 18
                    else random.choice(["employed", "unemployed"]),
                )

                # Set disability type only if PWD
                if member.is_pwd and not member.disability_type:
                    member.disability_type = "Visual Impairment"
                    member.save()

                self.stdout.write(
                    f"  Created member: {member.full_name} ({member.relationship_to_head})"
                )

        total = Resident.objects.count()
        self.stdout.write(self.style.SUCCESS(f"\nTotal residents created: {total}"))
        self.stdout.write(
            self.style.SUCCESS(f"Household heads: {len(household_heads)}")
        )
        self.stdout.write(
            self.style.SUCCESS(f"Household members: {total - len(household_heads)}")
        )
