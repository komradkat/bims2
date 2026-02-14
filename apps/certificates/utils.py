from django.conf import settings
from django.template.loader import render_to_string

def generate_pdf(template_name, context):
    """
    Renders an HTML template with context and converts it to PDF using WeasyPrint.
    """
    try:
        from weasyprint import HTML
    except OSError as e:
        raise ImportError(
            "WeasyPrint could not find its system dependencies (GTK). "
            "Please install GTK for Windows to enable PDF generation. "
            f"Original error: {str(e)}"
        )

    html_string = render_to_string(template_name, context)
    html = HTML(string=html_string, base_url=settings.BASE_DIR)
    
    # Optional: Add base CSS
    # css = CSS(string='@page { size: A4; margin: 1cm }')
    
    pdf_file = html.write_pdf()
    return pdf_file
