from django.shortcuts import get_object_or_404, redirect
from django.views.generic import ListView, DetailView, TemplateView
from django.contrib.auth.mixins import LoginRequiredMixin
from apps.core.mixins import NonBootstrapRequiredMixin
from apps.core.decorators import non_bootstrap_required
from django.contrib import messages
from django.utils import timezone
from django.http import HttpResponse
from .models import CertificateType, Certificate
from apps.business.models import BusinessPermit # Added for dual verification
from .forms import CertificateIssueForm
from .utils import generate_pdf
from apps.residents.models import Resident


class CertificatePrintView(LoginRequiredMixin, NonBootstrapRequiredMixin, DetailView):
    model = Certificate

    def get(self, request, *args, **kwargs):
        certificate = self.get_object()

        from apps.core.models import BarangayInfo, BarangayOfficial
        try:
            info = BarangayInfo.objects.get()
        except BarangayInfo.DoesNotExist:
            info = None

        # Try to find an active official as Punong Barangay / Captain
        captain_official = BarangayOfficial.objects.filter(
            position='punong_barangay', 
            is_active=True
        ).first()

        captain_name = 'PUNONG BARANGAY'
        captain_title = 'Punong Barangay'

        if captain_official:
            captain_name = captain_official.display_name.upper()
            captain_title = captain_official.get_position_display().split(' / ')[-1] # Prefer Barangay Captain if available
        elif info:
            captain_name = (info.captain_name or 'PUNONG BARANGAY').upper()
            captain_title = info.captain_title or 'Punong Barangay'

        barangay = {
            'name':          info.name if info else 'Barangay',
            'city':          info.city_municipality if info else '',
            'province':      info.province if info else '',
            'region':        info.region if info else '',
            'logo_url':      ('file:///' + info.logo.path.replace('\\', '/')) if (info and info.logo) else None,
            'captain_name':  captain_name,
            'captain_title': captain_title,
            'contact':       info.contact_number if info else '',
            'email':         info.email if info else '',
        }

        import os
        from django.conf import settings
        bp_path = os.path.join(settings.MEDIA_ROOT, 'barangay', 'logo', 'bangongpilipinas.png')
        bagong_pilipinas_url = ('file:///' + bp_path.replace('\\', '/')) if os.path.isfile(bp_path) else None

        context = {
            'certificate':        certificate,
            'barangay':           barangay,
            'today':              timezone.now(),
            'bagong_pilipinas_url': bagong_pilipinas_url,
        }

        template_name = certificate.certificate_type.template_file

        try:
            # 1. Reuse existing document if available and valid
            if certificate.document and certificate.digital_hash:
                try:
                    return HttpResponse(certificate.document.open('rb'), content_type='application/pdf')
                except Exception:
                    # If file is missing or error, regenerate
                    pass

            # 2. Generate PDF and calculate Hash
            pdf_content, pdf_hash = generate_pdf(template_name, context)
            
            # 3. Save Hash and Document if not draft
            if certificate.status != 'cancelled':
                certificate.digital_hash = pdf_hash
                
                # Save PDF content to a FileField
                from django.core.files.base import ContentFile
                from django.utils.text import slugify
                
                # Descriptive filename: LASTNAME-FIRSTNAME-TYPE-TRANSACTION.pdf
                res = certificate.resident
                name_slug = slugify(f"{res.last_name}-{res.first_name}")
                type_slug = certificate.certificate_type.slug
                txn = certificate.transaction_number
                filename = f"{name_slug}-{type_slug}-{txn}.pdf"
                
                certificate.document.save(filename, ContentFile(pdf_content), save=True)

            # 4. Return as Response
            response = HttpResponse(pdf_content, content_type='application/pdf')
            response['Content-Disposition'] = (
                f'inline; filename="{name_slug}-{type_slug}-{txn}.pdf"' if 'name_slug' in locals() 
                else f'inline; filename="{certificate.transaction_number}.pdf"'
            )
            return response
        except Exception as e:
            import traceback
            print(traceback.format_exc())
            messages.error(request, f"Error generating PDF: {e}")
            return redirect('certificates:center')


class CertificateCenterView(LoginRequiredMixin, NonBootstrapRequiredMixin, ListView):
    model = CertificateType
    template_name = 'pages/certificates/center.html'
    context_object_name = 'certificate_types'

    def get_queryset(self):
        return CertificateType.objects.filter(is_active=True).order_by('default_price', 'name')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'Certificate Issuance Center'
        
        if self.request.POST:
            context['issue_form'] = CertificateIssueForm(self.request.POST)
        else:
            context['issue_form'] = CertificateIssueForm()

        queryset = self.get_queryset()
        context['community_certs'] = queryset.filter(tier='community')
        context['pro_certs']       = queryset.filter(tier='pro')
        context['ultra_certs']     = queryset.filter(tier='ultra')

        preselect = self.request.GET.get('preselect')
        if preselect:
            try:
                cert = queryset.get(slug=preselect)
                context['preselect_cert'] = {
                    'id':      cert.id,
                    'name':    cert.name,
                    'slug':    cert.slug,
                    'price':   float(cert.default_price),
                    'is_free': cert.default_price == 0,
                }
                # Pre-fill form
                if not self.request.POST:
                    context['issue_form'].initial['certificate_type'] = cert.id
            except CertificateType.DoesNotExist:
                pass

        return context

    def post(self, request, *args, **kwargs):
        form = CertificateIssueForm(request.POST)
        if form.is_valid():
            certificate = form.save(commit=False)
            certificate.amount_paid = certificate.certificate_type.default_price
            certificate.status = 'issued'
            certificate.issued_by = request.user
            certificate.issued_at = timezone.now()
            certificate.save()

            messages.success(request, f"Successfully issued {certificate.certificate_type.name} for {certificate.resident.full_name}.")
            from django.urls import reverse
            return redirect(reverse('certificates:print', kwargs={'pk': certificate.pk}))
        else:
            messages.error(request, "Please fill in all required fields correctly.")
            return self.render_to_response(self.get_context_data())


class CertificateListView(LoginRequiredMixin, NonBootstrapRequiredMixin, ListView):
    model = Certificate
    template_name = 'pages/certificates/list.html'
    context_object_name = 'certificates'
    paginate_by = 50

    def get_queryset(self):
        queryset = Certificate.objects.all().select_related('resident', 'certificate_type', 'issued_by')
        search_query = self.request.GET.get('search', '').strip()
        if search_query:
            from django.db.models import Q
            queryset = queryset.filter(
                Q(transaction_number__icontains=search_query) |
                Q(resident__first_name__icontains=search_query)  |
                Q(resident__last_name__icontains=search_query)   |
                Q(or_number__icontains=search_query)
            )
        return queryset.order_by('-created_at')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'Issued Certificates Registry'
        return context


@non_bootstrap_required
def void_certificate(request, pk):
    if request.method == 'POST':
        certificate = get_object_or_404(Certificate, pk=pk)
        certificate.status = 'cancelled'
        certificate.save()
        messages.warning(request, f"Certificate {certificate.transaction_number} has been voided.")
    return redirect('certificates:list')


class VerifyDocumentView(TemplateView):
    """
    Public view for verifying certificate or permit authenticity via QR code.
    Exempt from typical auth mixes.
    """
    template_name = 'certificates/verify.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        tn = self.kwargs.get('tn')
        context['tn'] = tn
        context['valid'] = False

        # 1. Try Certificate Lookup
        try:
            cert = Certificate.objects.get(transaction_number=tn, status='issued')
            context.update({
                'valid': True,
                'type': cert.certificate_type.name,
                'recipient': cert.resident.full_name,
                'date_issued': cert.issued_at,
            })
            return context
        except Certificate.DoesNotExist:
            pass

        # 2. Try Business Permit Lookup
        try:
            permit = BusinessPermit.objects.get(permit_number=tn)
            context.update({
                'valid': True,
                'type': 'Business Permit',
                'recipient': f"{permit.business_name} (Owner: {permit.owner_name})",
                'date_issued': permit.issued_date,
            })
            return context
        except BusinessPermit.DoesNotExist:
            pass

        return context
