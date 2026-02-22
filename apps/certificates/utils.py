from django.conf import settings
from django.template.loader import render_to_string
from django.contrib.staticfiles import finders
import os
from io import BytesIO
from xhtml2pdf import pisa

def link_callback(uri, rel):
    """
    Convert HTML URIs to absolute system paths so xhtml2pdf can access those resources
    """
    sUrl = settings.STATIC_URL        # Typically /static/
    sRoot = settings.STATIC_ROOT      # Typically /home/userX/project_static/
    mUrl = settings.MEDIA_URL         # Typically /media/
    mRoot = settings.MEDIA_ROOT       # Typically /home/userX/project_static/media/

    # Handle Media Files
    if uri.startswith(mUrl):
        path = os.path.join(mRoot, uri.replace(mUrl, "", 1))
    
    # Handle Static Files
    elif uri.startswith(sUrl):
        relative_path = uri.replace(sUrl, "", 1)
        # Try finding it using Django finders (works in dev)
        found = finders.find(relative_path)
        if found:
            path = found
        else:
            # Fallback to STATIC_ROOT
            path = os.path.join(sRoot, relative_path)
    
    # Handle relative paths or other files
    else:
        found = finders.find(uri)
        if found:
            path = found
        else:
            return uri

    # make sure that file exists
    if not os.path.isfile(path):
        # Don't raise error, just return None or uri so xhtml2pdf ignores it gracefully
        # or print a warning
        print(f"Warning: URI not found: {uri} -> {path}")
        return uri
        
    return path

def generate_pdf(template_name, context):
    """
    Renders an HTML template with context and converts it to PDF using xhtml2pdf (ReportLab).
    Raises ValueError on pisa errors so callers get a useful message.
    """
    html_string = render_to_string(template_name, context)
    result = BytesIO()
    
    # Create the PDF
    pdf = pisa.pisaDocument(
        BytesIO(html_string.encode("UTF-8")),
        result,
        link_callback=link_callback
    )
    
    if pdf.err:
        import sys
        print(f"xhtml2pdf error(s) while rendering '{template_name}': {pdf.err}", file=sys.stderr)
        raise ValueError(f"PDF rendering failed for template '{template_name}' ({pdf.err} error(s)). Check server logs.")
        
    return result.getvalue()
