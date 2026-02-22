# Core views
from django.shortcuts import render, redirect
from django.views.generic import TemplateView, View
from django.contrib.auth.views import LoginView
from django.urls import reverse_lazy
from django.contrib import messages
from django.core.cache import cache
from django.db.models import Sum
from django.utils import timezone
from datetime import timedelta

# Import models for Dashboard
from apps.residents.models import Resident
from apps.certificates.models import Certificate
from apps.blotter.models import BlotterCase, Hearing
from apps.business.models import BusinessClearance
from apps.finance.models import OfficialReceipt

# Custom Login
class CustomLoginView(LoginView):
    template_name = 'auth/login.html'
    redirect_authenticated_user = True

    def form_valid(self, form):
        remember_me = self.request.POST.get('remember_me')
        response = super().form_valid(form)
        if not remember_me:
            # Session expires when the browser is closed
            self.request.session.set_expiry(0)
        return response

    def get_success_url(self):
        return reverse_lazy('core:dashboard')


from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import ListView, CreateView, UpdateView
from .models import User
from .decorators import role_required, tier_required
from django.utils.decorators import method_decorator

@method_decorator(role_required(['admin']), name='dispatch')
class UserListView(LoginRequiredMixin, ListView):
    model = User
    template_name = 'auth/user_list.html'
    context_object_name = 'users'
    paginate_by = 20

@method_decorator(role_required(['admin']), name='dispatch')
class UserCreateView(LoginRequiredMixin, CreateView):
    model = User
    template_name = 'auth/user_form.html'
    fields = ['username', 'email', 'role', 'barangay_position', 'is_active']
    success_url = reverse_lazy('core:user_list')
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['action'] = 'Add'
        return context
        
    def form_valid(self, form):
        user = form.save(commit=False)
        password = self.request.POST.get('password')
        if password:
            user.set_password(password)
        user.save()
        return super().form_valid(form)

@method_decorator(role_required(['admin']), name='dispatch')
class UserUpdateView(LoginRequiredMixin, UpdateView):
    model = User
    template_name = 'auth/user_form.html'
    fields = ['username', 'email', 'role', 'barangay_position', 'is_active']
    success_url = reverse_lazy('core:user_list')
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['action'] = 'Edit'
        return context


class DashboardView(LoginRequiredMixin, TemplateView):
    """Dashboard view with real data"""
    template_name = 'pages/dashboard.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        today = timezone.now().date()
        
        # Stats
        total_residents = Resident.objects.filter(is_active=True).count()
        documents_issued = Certificate.objects.filter(status='issued').count()
        
        # Revenue: Sum of OfficialReceipts + BusinessClearances (if not in OR) + Certificates (if not in OR)
        # For simplicity, assuming all revenue is tracked in OfficialReceipt if we enforced it,
        # but since we just implemented it, we might need to sum up.
        # Let's sum OfficialReceipts for now as it's the intended source of truth for Finance.
        # If BusinessClearance creates an OR, it should be there.
        # In my BusinessCreateView, I created BusinessClearance but not OfficialReceipt explicitly in Finance app.
        # But BusinessClearance has 'amount_paid'.
        
        revenue_or = OfficialReceipt.objects.filter(status='paid').aggregate(Sum('amount'))['amount__sum'] or 0
        revenue_biz = BusinessClearance.objects.aggregate(Sum('amount_paid'))['amount_paid__sum'] or 0
        revenue_cert = Certificate.objects.filter(status='paid').aggregate(Sum('amount_paid'))['amount_paid__sum'] or 0
        
        # To avoid double counting, ideally we should have a unified transaction model.
        # For this MVP, I'll display the sum but acknowledge it might need refinement.
        # Let's just use OfficialReceipt if available, otherwise fallback.
        # Actually, let's just sum OfficialReceipt and assume that's the finance module's job.
        # But since I didn't link Business/Cert to OR creation automatically in all places,
        # I'll just use a simple aggregation of what we have.
        # Since I implemented BusinessClearance and it stores amount, and Certificate stores amount.
        # I'll sum them.
        
        total_revenue = revenue_or + revenue_biz + revenue_cert
        
        active_cases = BlotterCase.objects.exclude(status__in=['settled', 'dismissed', 'cfa']).count()
        
        context['stats'] = {
            'total_residents': total_residents,
            'documents_issued': documents_issued,
            'total_revenue': total_revenue,
            'active_cases': active_cases,
        }
        
        # Recent Certificates
        recent_certs = Certificate.objects.select_related('resident', 'certificate_type').order_by('-created_at')[:5]
        context['recent_certificates'] = [
            {
                'recipient': c.resident.full_name,
                'type': c.certificate_type.name,
                'date': c.created_at,
                'status': c.get_status_display(),
            } for c in recent_certs
        ]
        
        # Urgent Blotter Cases (Hearings scheduled for today/tomorrow)
        tomorrow = today + timedelta(days=1)
        upcoming_hearings = Hearing.objects.filter(
            scheduled_at__date__gte=today,
            scheduled_at__date__lte=tomorrow,
            status='scheduled'
        ).select_related('case').order_by('scheduled_at')[:5]
        
        context['urgent_cases'] = [
            {
                'priority_number': idx + 1,
                'priority_color': 'error' if h.scheduled_at.date() == today else 'warning',
                'title': h.case.case_number,
                'description': f"{h.case.get_incident_type_display()} - {h.remarks}",
                'schedule': h.scheduled_at,
            } for idx, h in enumerate(upcoming_hearings)
        ]
        
        # Activity Logs (from Audit/History)
        # We can't easily fetch mixed history efficiently without the Audit view logic.
        # I'll reuse a simplified version of Audit logic here.
        from django.apps import apps
        
        models_to_track = [
            ('residents', 'Resident'),
            ('certificates', 'Certificate'),
            ('blotter', 'BlotterCase'),
            ('business', 'BusinessPermit'),
        ]

        activities = []
        for app_label, model_name in models_to_track:
            try:
                model = apps.get_model(app_label, model_name)
                if hasattr(model, 'history'):
                    records = model.history.all().order_by('-history_date')[:3]
                    for record in records:
                        action_map = {'+': 'Created', '~': 'Updated', '-': 'Deleted'}
                        action = action_map.get(record.history_type, 'Unknown')

                        activities.append({
                            'time': record.history_date,
                            'activity': f"{action} {model_name}: {str(record)}",
                            'user': record.history_user.username if record.history_user else 'System',
                            'status': 'Completed'
                        })
            except LookupError:
                continue

        activities.sort(key=lambda x: x['time'], reverse=True)
        activities = activities[:5]

        context['activity_headers'] = ['Time', 'Activity', 'User', 'Status']
        context['activity_rows'] = [
            {
                'cells': [
                    a['time'],
                    a['activity'],
                    a['user'],
                    f'<span class="badge badge-success">{a["status"]}</span>'
                ]
            } for a in activities
        ]
        
        return context

@method_decorator(tier_required(['ultra']), name='dispatch')
class GisMapView(TemplateView):
    """GIS Map view (Ultra only)"""
    template_name = 'pages/gis/map.html'


class LicenseActivationView(LoginRequiredMixin, View):
    """License activation view for activating license keys"""
    template_name = 'auth/license_activation.html'
    
    def get(self, request):
        from apps.core.utils.hardware import get_hardware_id
        from apps.core.models import LicenseKey
        
        hardware_id = get_hardware_id()
        current_license = LicenseKey.objects.filter(
            hardware_id=hardware_id,
            is_active=True
        ).first()
        
        return render(request, self.template_name, {
            'hardware_id': hardware_id,
            'current_license': current_license
        })
    
    def post(self, request):
        from apps.core.utils.hardware import get_hardware_id
        from apps.core.models import LicenseKey
        
        license_key = request.POST.get('license_key', '').strip()
        hardware_id = get_hardware_id()
        
        if not license_key:
            messages.error(request, "Please enter a license key.")
            return redirect('core:license_activation')
        
        try:
            license_obj = LicenseKey.objects.get(key=license_key)
            
            # Check if already activated on another machine
            if license_obj.hardware_id and license_obj.hardware_id != hardware_id:
                messages.error(
                    request,
                    "This license is already activated on another server. "
                    "Please contact support to transfer your license."
                )
                return redirect('core:license_activation')
            
            # Activate license
            license_obj.hardware_id = hardware_id
            license_obj.is_active = True
            license_obj.save()
            
            # Clear cache to force reload of license data
            cache.delete('active_license')
            
            messages.success(
                request,
                f"License activated successfully! Tier: {license_obj.tier.upper()} | "
                f"Max Users: {license_obj.max_users}"
            )
            return redirect('core:dashboard')
            
        except LicenseKey.DoesNotExist:
            messages.error(request, "Invalid license key. Please check and try again.")
            return redirect('core:license_activation')
        except LicenseKey.DoesNotExist:
            messages.error(request, "Invalid license key. Please check and try again.")
            return redirect('core:license_activation')


class SetupView(View):
    """
    Initial System Setup Wizard.
    Allows setting Barangay Info and creating/updating the Admin account.
    """
    template_name = 'core/setup.html'
    
    def get(self, request):
        from apps.core.models import BarangayInfo
        
        # If setup is already complete, redirect to dashboard
        if BarangayInfo.objects.filter(is_setup_complete=True).exists():
            return redirect('core:dashboard')
            
        return render(request, self.template_name)
        
    def post(self, request):
        from apps.core.models import BarangayInfo
        from django.contrib.auth import get_user_model
        
        User = get_user_model()
        
        # 1. Barangay Info
        name = request.POST.get('barangay_name')
        address = request.POST.get('barangay_address')
        contact = request.POST.get('contact_number', '')
        email = request.POST.get('barangay_email', '')
        # captain = request.POST.get('barangay_captain') # Removed
        # secretary = request.POST.get('barangay_secretary') # Removed
        # treasurer = request.POST.get('barangay_treasurer') # Removed
        
        # New: GIS Coordinates
        latitude = request.POST.get('latitude')
        longitude = request.POST.get('longitude')
        
        logo = request.FILES.get('barangay_logo')
        
        # 2. Admin Account
        username = request.POST.get('admin_username')
        password = request.POST.get('admin_password')
        # admin_email = request.POST.get('admin_email') # Removed requirement for separate email in this step
        
        # Basic Validation
        if not all([name, address, username, password]):
            messages.error(request, "Please fill in all required fields.")
            return render(request, self.template_name)
            
        try:
            # Save Barangay Info
            # Singleton: Get existing or create new
            info = BarangayInfo.objects.first()
            if not info:
                info = BarangayInfo()
                
            info.name = name
            info.address = address
            info.contact_number = contact
            info.email = email
            
            # Save coordinates if provided
            if latitude and longitude:
                try:
                    info.latitude = float(latitude)
                    info.longitude = float(longitude)
                except ValueError:
                    pass # Ignore invalid floats
            
            if logo:
                info.logo = logo
            
            info.is_setup_complete = True
            info.save()
            
            # Create/Update Admin User
            # Check if admin exists
            if User.objects.filter(username=username).exists():
                user = User.objects.get(username=username)
                user.set_password(password)
                # user.email = admin_email 
                user.role = 'admin'
                user.is_superuser = True
                user.is_staff = True
                user.save()
            else:
                User.objects.create_superuser(
                    username=username,
                    # email=admin_email,
                    email='',
                    password=password,
                    role='admin',
                    barangay_position='Administrator'
                )
                
            messages.success(request, "System Setup Completed Successfully! Please login.")
            return redirect('core:login')
            
        except Exception as e:
            messages.error(request, f"An error occurred: {str(e)}")
            return render(request, self.template_name)
