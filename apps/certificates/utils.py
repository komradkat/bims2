import qrcode
import hashlib
import base64
import os
from io import BytesIO
from django.conf import settings
from django.template.loader import render_to_string
import weasyprint


def _url_fetcher(url):
    """
    Maps Django /static/ and /media/ URLs to local file paths for WeasyPrint.
    """
    from django.contrib.staticfiles import finders

    static_url = settings.STATIC_URL
    media_url = settings.MEDIA_URL

    if url.startswith("file://"):
        return weasyprint.default_url_fetcher(url)

    path = None

    if url.startswith(media_url):
        path = os.path.join(settings.MEDIA_ROOT, url[len(media_url) :])
    elif url.startswith(static_url):
        relative = url[len(static_url) :]
        found = finders.find(relative)
        if found:
            path = found
        elif hasattr(settings, "STATIC_ROOT") and settings.STATIC_ROOT:
            path = os.path.join(settings.STATIC_ROOT, relative)

    if path and os.path.isfile(path):
        with open(path, "rb") as f:
            return {"file_obj": BytesIO(f.read()), "mime_type": None}

    return weasyprint.default_url_fetcher(url)


def generate_qr_code(data):
    """
    Generates a QR code image and returns it as a base64 string for HTML embedding.
    """
    qr = qrcode.QRCode(
        version=1,
        error_correction=qrcode.constants.ERROR_CORRECT_L,
        box_size=10,
        border=0,
    )
    qr.add_data(data)
    qr.make(fit=True)

    img = qr.make_image(fill_color="black", back_color="white")

    buffered = BytesIO()
    img.save(buffered, format="PNG")
    return base64.b64encode(buffered.getvalue()).decode()


def generate_pdf(template_name, context):
    """
    Renders a Django template and converts it to PDF using WeasyPrint.
    Returns (pdf_bytes, sha256_hash).
    """
    # 1. Generate QR Code if transaction_number exists in context
    cert_obj = context.get("certificate")
    if cert_obj and hasattr(cert_obj, "transaction_number"):
        # Generate the absolute verification URL
        from django.urls import reverse

        host = (
            context.get("request").get_host()
            if context.get("request")
            else "localhost:8000"
        )
        scheme = "https" if not settings.DEBUG else "http"
        verify_url = f"{scheme}://{host}{reverse('certificates:verify', kwargs={'tn': cert_obj.transaction_number})}"

        context["qr_code_base64"] = generate_qr_code(verify_url)

    # 2. Render Template
    html_string = render_to_string(template_name, context)
    base_url = f"file:///{settings.BASE_DIR}/"

    # 3. Generate PDF
    try:
        pdf_bytes = weasyprint.HTML(
            string=html_string, base_url=base_url, url_fetcher=_url_fetcher
        ).write_pdf()
    except Exception as exc:
        raise ValueError(f"PDF rendering failed for '{template_name}': {exc}") from exc

    # 4. Calculate SHA256 Hash
    sha256_hash = hashlib.sha256(pdf_bytes).hexdigest()

    return pdf_bytes, sha256_hash
