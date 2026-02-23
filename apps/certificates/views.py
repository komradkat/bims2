from django.shortcuts import get_object_or_404, redirect
from django.views.generic import ListView, DetailView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib import messages
from django.utils import timezone
from django.http import HttpResponse
from .models import CertificateType, Certificate
from .utils import generate_pdf
from apps.residents.models import Resident


class CertificatePrintView(LoginRequiredMixin, DetailView):
    model = Certificate

    def get(self, request, *args, **kwargs):
        certificate = self.get_object()

        from apps.core.models import BarangayInfo
        try:
            info = BarangayInfo.objects.get()
        except BarangayInfo.DoesNotExist:
            info = None

        barangay = {
            'name':         info.name if info else 'Barangay',
            'city':         info.city_municipality if info else '',
            'province':     info.province if info else '',
            'region':       info.region if info else '',
            'logo_url':     ('file:///' + info.logo.path.replace('\\', '/')) if (info and info.logo) else None,
            'captain_name': (info.captain_name or '').upper() if info else 'PUNONG BARANGAY',
            'contact':      info.contact_number if info else '',
            'email':        info.email if info else '',
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
            pdf = generate_pdf(template_name, context)
            response = HttpResponse(pdf, content_type='application/pdf')
            response['Content-Disposition'] = (
                f'inline; filename="{certificate.transaction_number}.pdf"'
            )
            return response
        except Exception as e:
            messages.error(request, f"Error generating PDF: {e}")
            return redirect('certificates:center')


class CertificateCenterView(LoginRequiredMixin, ListView):
    model = CertificateType
    template_name = 'pages/certificates/center.html'
    context_object_name = 'certificate_types'

    def get_queryset(self):
        return CertificateType.objects.filter(is_active=True).order_by('default_price', 'name')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'Certificate Issuance Center'

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
            except CertificateType.DoesNotExist:
                pass

        return context

    def post(self, request, *args, **kwargs):
        resident_id  = request.POST.get('resident')
        cert_type_id = request.POST.get('certificate_type')
        purpose      = request.POST.get('purpose')
        or_number    = request.POST.get('or_number', '')

        if not all([resident_id, cert_type_id, purpose]):
            messages.error(request, "Please fill in all required fields.")
            return redirect('certificates:center')

        resident  = get_object_or_404(Resident, id=resident_id)
        cert_type = get_object_or_404(CertificateType, id=cert_type_id)

        certificate = Certificate.objects.create(
            resident=resident,
            certificate_type=cert_type,
            purpose=purpose,
            or_number=or_number,
            amount_paid=cert_type.default_price,
            status='issued',
            issued_by=request.user,
            issued_at=timezone.now(),
        )

        messages.success(request, f"Successfully issued {cert_type.name} for {resident.full_name}.")
        from django.urls import reverse
        return redirect(reverse('certificates:print', kwargs={'pk': certificate.pk}))


class CertificateListView(LoginRequiredMixin, ListView):
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


def void_certificate(request, pk):
    if request.method == 'POST':
        certificate = get_object_or_404(Certificate, pk=pk)
        certificate.status = 'cancelled'
        certificate.save()
        messages.warning(request, f"Certificate {certificate.transaction_number} has been voided.")
    return redirect('certificates:list')
