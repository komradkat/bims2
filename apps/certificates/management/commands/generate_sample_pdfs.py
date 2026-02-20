from django.core.management.base import BaseCommand
from django.utils import timezone
from apps.certificates.models import CertificateType, Certificate
from apps.residents.models import Resident
from apps.certificates.utils import generate_pdf
import os
from django.conf import settings

class Command(BaseCommand):
    help = 'Generate sample PDFs for all certificate types'

    def handle(self, *args, **kwargs):
        self.stdout.write('Generating sample PDFs...')
        
        # Ensure output directory exists
        output_dir = os.path.join(settings.MEDIA_ROOT, 'sample_pdfs')
        os.makedirs(output_dir, exist_ok=True)
        
        import traceback
        
        # Create dummy resident as a DICT to avoid lookup issues
        resident = {
            'first_name': 'Juan',
            'last_name': 'Dela Cruz',
            'middle_name': 'Santos',
            'age': 25,
            'sex': 'M',
            'civil_status': 'single',
            'get_civil_status_display': 'Single',
            'citizenship': 'Filipino',
            'address': 'Purok 1, Barangay San Jose',
            'is_household_head': True,
            'full_name': 'Juan Santos Dela Cruz',
        }
        
        # Get all certificate types
        types = CertificateType.objects.filter(is_active=True)
        
        for cert_type in types:
            try:
                # Create dummy certificate context as DICT
                cert = {
                    'certificate_type': cert_type, # Model instance is fine here
                    'resident': resident,
                    'purpose': 'Employment Requirement',
                    'transaction_number': f'SAMPLE-{cert_type.slug.upper()}',
                    'or_number': 'OR-12345',
                    'issued_at': timezone.now(),
                    'issued_by': {
                        'username': 'admin',
                        'get_full_name': 'Admin User'
                    }
                }
                
                # Mock context
                logo_path = '/media/barangay/logo/445493360_7676135385787063_8483044850165205000_n-removebg-preview.png'
                context = {
                    'certificate': cert,
                    'barangay': {
                        'name': 'San Jose',
                        'city': 'San Fernando',
                        'province': 'Pampanga',
                        'logo_url': logo_path
                    },
                    'barangay_info': {
                        'name': 'San Jose',
                        'city': 'San Fernando',
                        'province': 'Pampanga',
                        'logo_url': logo_path
                    },
                    'today': timezone.now(),
                }
                
                # Generate PDF logic from utils (modified to accept context directly if needed)
                from django.template.loader import render_to_string
                
                html_content = render_to_string(cert_type.template_file, context)
                
                # Always save HTML for debugging/preview
                html_filename = f"{cert_type.slug}_preview.html"
                html_filepath = os.path.join(output_dir, html_filename)
                with open(html_filepath, 'w', encoding='utf-8') as f:
                    f.write(html_content)
                self.stdout.write(f'Generated properties: {html_filepath}')

                try:
                    pdf_content = generate_pdf(cert_type.template_file, context)
                    filename = f"{cert_type.slug}_sample.pdf"
                    filepath = os.path.join(output_dir, filename)
                    with open(filepath, 'wb') as f:
                        f.write(pdf_content)
                    self.stdout.write(self.style.SUCCESS(f'Generated PDF: {filepath}'))
                except Exception as e:
                    self.stdout.write(self.style.WARNING(f'PDF generation failed: {str(e)}'))
                    self.stdout.write(self.style.SUCCESS(f'HTML Preview available: {html_filepath}'))
                    # traceback.print_exc() # Optional: uncomment for details

                # --- Docx Generation ---
                try:
                    from docxtpl import DocxTemplate
                    docx_template_path = os.path.join(settings.MEDIA_ROOT, 'templates', 'certificate_template.docx')
                    
                    if os.path.exists(docx_template_path):
                        doc = DocxTemplate(docx_template_path)
                        
                        # Docx Context (flatter structure usually better for simple templates)
                        docx_context = {
                            'province': 'Pampanga',
                            'city': 'San Fernando',
                            'barangay_name': 'San Jose',
                            'certificate_title': cert_type.name.upper(),
                            'full_name': resident['full_name'],
                            'citizenship': resident['citizenship'],
                            'address': resident['address'],
                            'purpose': context['certificate']['purpose'],
                            'day': context['today'].strftime('%d'),
                            'month_year': context['today'].strftime('%B, %Y'),
                        }
                        
                        doc.render(docx_context)
                        
                        docx_filename = f"{cert_type.slug}_sample.docx"
                        docx_filepath = os.path.join(output_dir, docx_filename)
                        doc.save(docx_filepath)
                        self.stdout.write(self.style.SUCCESS(f'Generated DOCX: {docx_filepath}'))
                    else:
                        self.stdout.write(self.style.WARNING(f'Skipping DOCX: Template not found at {docx_template_path}'))
                        
                except Exception as e:
                    self.stdout.write(self.style.ERROR(f'Failed to generate DOCX for {cert_type.name}: {str(e)}'))
                
            except Exception as e:
                self.stdout.write(self.style.ERROR(f'Failed to generate {cert_type.name}: {str(e)}'))
                traceback.print_exc()

        self.stdout.write(self.style.SUCCESS(f'\nAll samples (HTML/PDF) saved to: {output_dir}'))
