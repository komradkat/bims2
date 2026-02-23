from django.conf import settings
from django.template.loader import render_to_string
import os
from io import BytesIO

import weasyprint


def _url_fetcher(url):
    """
    Maps Django /static/ and /media/ URLs to local file paths for WeasyPrint.
    """
    from django.contrib.staticfiles import finders

    static_url = settings.STATIC_URL
    media_url  = settings.MEDIA_URL

    if url.startswith("file://"):
        return weasyprint.default_url_fetcher(url)

    path = None

    if url.startswith(media_url):
        path = os.path.join(settings.MEDIA_ROOT, url[len(media_url):])
    elif url.startswith(static_url):
        relative = url[len(static_url):]
        found = finders.find(relative)
        if found:
            path = found
        elif hasattr(settings, "STATIC_ROOT") and settings.STATIC_ROOT:
            path = os.path.join(settings.STATIC_ROOT, relative)

    if path and os.path.isfile(path):
        with open(path, "rb") as f:
            return {"file_obj": BytesIO(f.read()), "mime_type": None}

    return weasyprint.default_url_fetcher(url)


def generate_pdf(template_name, context):
    """
    Renders a Django template and converts it to PDF using WeasyPrint.
    Supports full CSS: flex, grid, border-radius, position:absolute, etc.
    Returns bytes.
    """
    html_string = render_to_string(template_name, context)
    base_url = f"file:///{settings.BASE_DIR}/"

    try:
        pdf_bytes = (
            weasyprint.HTML(string=html_string, base_url=base_url, url_fetcher=_url_fetcher)
            .write_pdf()
        )
    except Exception as exc:
        raise ValueError(f"PDF rendering failed for '{template_name}': {exc}") from exc

    return pdf_bytes
