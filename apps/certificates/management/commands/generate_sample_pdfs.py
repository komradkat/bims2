import os
from django.core.management.base import BaseCommand
from django.utils import timezone
from django.conf import settings
from django.template.loader import render_to_string
from apps.certificates.models import CertificateType
from apps.certificates.utils import generate_pdf


class Command(BaseCommand):
    help = "Generate sample PDFs for all certificate types"

    def handle(self, *args, **kwargs):
        self.stdout.write("Generating sample PDFs with context sync...")

        # Ensure output directory exists
        output_dir = os.path.join(settings.MEDIA_ROOT, "sample_pdfs")
        os.makedirs(output_dir, exist_ok=True)

        # 1. Fetch Real Barangay Info or fall back
        from apps.core.models import BarangayInfo

        try:
            info = BarangayInfo.objects.get()
            barangay_data = {
                "name": info.name,
                "city": info.city_municipality,
                "province": info.province,
                "region": info.region,
                "logo_url": ("file:///" + info.logo.path.replace("\\", "/"))
                if info.logo
                else None,
                "captain_name": (info.captain_name or "").upper()
                if hasattr(info, "captain_name")
                else "PUNONG BARANGAY",
                "contact": info.contact_number,
                "email": info.email,
            }
        except Exception:
            self.stdout.write(
                self.style.WARNING("No BarangayInfo found, using mock data.")
            )
            barangay_data = {
                "name": "SAMPLE BARANGAY",
                "city": "SAMPLE CITY",
                "province": "SAMPLE PROVINCE",
                "logo_url": None,
                "captain_name": "JUAN DELA CRUZ",
            }

        # 2. Get System Version (Global Context)
        system_version = getattr(settings, "BIMS_VERSION", "1.0.0-dev")

        # 3. Create dummy resident
        resident = {
            "first_name": "Juan",
            "last_name": "Dela Cruz",
            "middle_name": "Santos",
            "age": 25,
            "sex": "M",
            "get_civil_status_display": "Single",
            "citizenship": "Filipino",
            "address": "Purok 1, Barangay Sample",
            "full_name": "Juan Santos Dela Cruz",
        }

        # 4. Process all active certificate types
        types = CertificateType.objects.filter(is_active=True)

        bp_path = os.path.join(
            settings.MEDIA_ROOT, "barangay", "logo", "bangongpilipinas.png"
        )
        bagong_pilipinas_url = (
            ("file:///" + bp_path.replace("\\", "/"))
            if os.path.isfile(bp_path)
            else None
        )

        for cert_type in types:
            try:
                # Mock certificate instance attributes
                class MockCert:
                    pass

                cert = MockCert()
                cert.certificate_type = cert_type
                cert.resident = resident
                cert.purpose = "Sample Purpose for Testing"
                cert.transaction_number = f"SAMPLE-{cert_type.slug.upper()}"
                cert.or_number = "OR-SAMPLE"
                cert.issued_at = timezone.now()
                cert.status = "issued"  # Ensure it gets hashed
                cert.digital_hash = "(Sample Hash)"  # Placeholder for preview
                cert.id = 999

                context = {
                    "certificate": cert,
                    "barangay": barangay_data,
                    "today": timezone.now(),
                    "system_version": system_version,
                    "bagong_pilipinas_url": bagong_pilipinas_url,
                }

                # HTML Preview for debugging
                html_content = render_to_string(cert_type.template_file, context)
                html_filename = f"{cert_type.slug}_preview.html"
                with open(
                    os.path.join(output_dir, html_filename), "w", encoding="utf-8"
                ) as f:
                    f.write(html_content)

                # PDF Generation
                try:
                    pdf_content, pdf_hash = generate_pdf(
                        cert_type.template_file, context
                    )

                    pdf_filename = f"{cert_type.slug}_sample.pdf"
                    filepath = os.path.join(output_dir, pdf_filename)
                    with open(filepath, "wb") as f:
                        f.write(pdf_content)

                    self.stdout.write(
                        self.style.SUCCESS(
                            f"Generated PDF: {pdf_filename} | Hash: {pdf_hash[:10]}..."
                        )
                    )
                except Exception as e:
                    self.stdout.write(
                        self.style.ERROR(f"PDF Error for {cert_type.slug}: {str(e)}")
                    )
                    # self.stdout.write(traceback.format_exc())

            except Exception as e:
                self.stdout.write(
                    self.style.ERROR(f"Failed to process {cert_type.name}: {str(e)}")
                )

        self.stdout.write(self.style.SUCCESS(f"\nSamples saved to: {output_dir}"))
