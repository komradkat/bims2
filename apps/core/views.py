# Core views
from django.shortcuts import render, redirect
from django.http import HttpResponse, HttpResponseRedirect
from django.views.generic import TemplateView, View, ListView, CreateView, UpdateView
from django.contrib.auth.views import LoginView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth import get_user_model, update_session_auth_hash
from django.urls import reverse_lazy, reverse
from django.contrib import messages
from django.core.cache import cache
from django.db.models import Sum, Q
from django.utils import timezone
from django.utils.safestring import mark_safe
from datetime import timedelta
import json

# Import models for Dashboard
from .models import Notification
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



from .models import User, Notification, BarangayOfficial
from .decorators import role_required, tier_required
from django.utils.decorators import method_decorator

@method_decorator(role_required(['admin']), name='dispatch')
class UserListView(LoginRequiredMixin, ListView):
    model = User
    template_name = 'auth/user_list.html'
    context_object_name = 'users'
    paginate_by = 20
    ordering = ['id']

@method_decorator(role_required(['admin']), name='dispatch')
class UserCreateView(LoginRequiredMixin, CreateView):
    model = User
    template_name = 'auth/user_form.html'
    fields = ['username', 'first_name', 'last_name', 'email', 'role', 'barangay_position', 'official', 'is_active']
    success_url = reverse_lazy('core:user_list')
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['action'] = 'Add'
        
        # Get requested official ID (if any) from GET parameter
        official_id = self.request.GET.get('official_id')
        
        # Show all officials in serialized data to ensure auto-population works even if 
        # the official doesn't meet filter criteria (e.g. inactive)
        all_officials = BarangayOfficial.objects.all()
        # For the dropdown, we want unlinked ones, BUT always include the specifically requested one
        q = Q(user_account__isnull=True)
        if official_id:
            try:
                q |= Q(id=int(official_id))
            except (ValueError, TypeError):
                pass
            
        context['officials'] = all_officials.filter(q)
        
        # Serialize ALL for Alpine.js so we can ALWAYS auto-populate if an ID is passed
        officials_data = {
            str(off.id): {
                'first_name': off.first_name,
                'last_name': off.last_name,
                'email': off.email,
                'position': off.get_position_display(),
            } for off in all_officials
        }
        context['officials_json'] = json.dumps(officials_data)
        
        if official_id:
            context['preselected_official_id'] = str(official_id)
            
        return context
        
    def form_valid(self, form):
        user = form.save(commit=False)
        password = self.request.POST.get('password')
        if password:
            user.set_password(password)
        
        # Link as Bootstrap logic
        link_as_bootstrap = self.request.POST.get('link_as_bootstrap') == 'on'
        if link_as_bootstrap and self.request.user.is_bootstrap:
            # Transfer official to current user AND update credentials
            self.request.user.username = user.username
            self.request.user.email = user.email
            self.request.user.official = user.official
            self.request.user.role = user.role
            self.request.user.barangay_position = user.barangay_position
            self.request.user.is_bootstrap = False
            
            # Sync data from official if linked
            if user.official:
                self.request.user.first_name = user.official.first_name
                self.request.user.last_name = user.official.last_name
                self.request.user.email = user.official.email
                self.request.user.barangay_position = user.official.get_position_display()
            
            if password:
                self.request.user.set_password(password)
            
            self.request.user.save()
            
            # Update session hash to prevent logout
            update_session_auth_hash(self.request, self.request.user)
            
            messages.success(self.request, f"Account '{self.request.user.username}' successfully linked to Official: {self.request.user.official.full_name}. You are no longer in bootstrap mode.")
            return redirect('core:profile')

        # Sync data from official if linked and fields were left empty
        if user.official:
            if not user.first_name:
                user.first_name = user.official.first_name
            if not user.last_name:
                user.last_name = user.official.last_name
            if not user.email:
                user.email = user.official.email
            if not user.barangay_position:
                user.barangay_position = user.official.get_position_display()

        user.save()
        messages.success(self.request, f"User {user.username} created successfully.")
        self.object = user
        return HttpResponseRedirect(self.get_success_url())

@method_decorator(role_required(['admin']), name='dispatch')
class UserUpdateView(LoginRequiredMixin, UpdateView):
    model = User
    template_name = 'auth/user_form.html'
    fields = ['username', 'first_name', 'last_name', 'email', 'role', 'barangay_position', 'official', 'is_active']
    success_url = reverse_lazy('core:user_list')
    
    def form_valid(self, form):
        user = form.save(commit=False)
        
        # Sync data from official if linked and fields were left empty (or locked)
        if user.official:
            if not user.first_name:
                user.first_name = user.official.first_name
            if not user.last_name:
                user.last_name = user.official.last_name
            if not user.email:
                user.email = user.official.email
            if not user.barangay_position:
                user.barangay_position = user.official.get_position_display()
        
        user.save()
        messages.success(self.request, f"User {user.username} updated successfully.")
        return HttpResponseRedirect(self.get_success_url())

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['action'] = 'Edit'
        
        all_officials = BarangayOfficial.objects.all()
        # Show all officials but prioritize the currently linked one
        eligible_officials = all_officials.filter(
            Q(user_account__isnull=True) | Q(user_account=self.object)
        )
        context['officials'] = eligible_officials
        
        # Serialize ALL for Alpine.js auto-population
        officials_data = {
            str(off.id): {
                'first_name': off.first_name,
                'last_name': off.last_name,
                'email': off.email,
                'position': off.get_position_display(),
            } for off in all_officials
        }
        context['officials_json'] = json.dumps(officials_data)
        
        if self.object.official:
            context['preselected_official_id'] = str(self.object.official.id)
            
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
        # Let's sum OfficialReceipts for now as it's the intended source of truth for Finance.
        # If BusinessClearance creates an OR, it should be there.
        # In my BusinessCreateView, I created BusinessClearance but not OfficialReceipt explicitly in Finance app.
        # But BusinessClearance has 'amount_paid'.
        
        # Revenue Calculation (Pro/Ultra feature optimization)
        total_revenue = 0
        license_tier = getattr(self.request, 'license', {}).get('tier', 'community')
        
        if license_tier in ['pro', 'ultra']:
            revenue_or = OfficialReceipt.objects.filter(status='paid').aggregate(Sum('amount'))['amount__sum'] or 0
            revenue_biz = BusinessClearance.objects.aggregate(Sum('amount_paid'))['amount_paid__sum'] or 0
            revenue_cert = Certificate.objects.filter(status='paid').aggregate(Sum('amount_paid'))['amount_paid__sum'] or 0
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
                    # Fix N+1 by selecting history_user
                    records = model.history.select_related('history_user').all().order_by('-history_date')[:5]
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
                    a['status']
                ],
                'status_class': 'badge-success' if a['status'] == 'Completed' else 'badge-ghost'
            } for a in activities
        ]
        
        return context

@method_decorator(role_required(['admin']), name='dispatch')
class SettingsView(LoginRequiredMixin, View):
    """View to manage Barangay Information and System Settings"""
    template_name = 'core/settings.html'

    def get(self, request):
        from apps.core.models import BarangayInfo, BarangayOfficial
        info = BarangayInfo.objects.first()
        captain = BarangayOfficial.objects.filter(position='punong_barangay', is_active=True).first()
        return render(request, self.template_name, {'info': info, 'captain': captain})

    def post(self, request):
        from apps.core.models import BarangayInfo
        info = BarangayInfo.objects.first() or BarangayInfo()
        
        info.name = request.POST.get('barangay_name')
        info.street = request.POST.get('barangay_street', '')
        info.city_municipality = request.POST.get('barangay_city_municipality', '')
        info.province = request.POST.get('barangay_province', '')
        info.region = request.POST.get('region', '')
        info.zip_code = request.POST.get('zip_code', '')
        info.contact_number = request.POST.get('contact_number', '')
        info.email = request.POST.get('barangay_email', '')
        # captain_name & captain_title are auto-synced from the officials roster
        
        if request.POST.get('latitude'):
            info.latitude = float(request.POST.get('latitude'))
        if request.POST.get('longitude'):
            info.longitude = float(request.POST.get('longitude'))
            
        if request.FILES.get('barangay_logo'):
            info.logo = request.FILES['barangay_logo']
            
        info.save()

        # Keep the Barangay Hall blip in sync with settings
        try:
            from apps.gis.models import EmergencyService
            hall_defaults = {
                'name': f"{info.name} — Barangay Hall",
                'address': info.full_address or '',
                'contact_number': info.contact_number or '',
                'description': f"Official Barangay Hall of {info.name}.",
                'icon_emoji': '🏛️',
                'is_active': True,
            }
            if info.latitude and info.longitude:
                hall_defaults['latitude'] = info.latitude
                hall_defaults['longitude'] = info.longitude
            EmergencyService.objects.update_or_create(
                service_type='hall',
                defaults=hall_defaults,
            )
        except Exception:
            pass  # Non-fatal

        messages.success(request, "System settings updated successfully.")
        return redirect('core:settings')

@method_decorator(tier_required(['ultra']), name='dispatch')
class GisMapView(LoginRequiredMixin, TemplateView):
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


class LicenseInfoView(LoginRequiredMixin, TemplateView):
    """View to display detailed license and hardware information"""
    template_name = 'auth/license_info.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'License Information'
        return context


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
        street = request.POST.get('barangay_street', '')
        city_municipality = request.POST.get('barangay_city_municipality')
        province = request.POST.get('barangay_province')
        region = request.POST.get('barangay_region', '')
        zip_code = request.POST.get('barangay_zip_code', '')
        contact = request.POST.get('contact_number', '')
        email = request.POST.get('barangay_email', '')
        
        # New: GIS Coordinates
        latitude = request.POST.get('latitude')
        longitude = request.POST.get('longitude')
        
        logo = request.FILES.get('barangay_logo')
        
        # 2. Admin Account
        username = request.POST.get('admin_username')
        password = request.POST.get('admin_password')
        # admin_email = request.POST.get('admin_email') # Removed requirement for separate email in this step
        
        # Basic Validation
        if not all([name, city_municipality, province, username, password]):
            messages.error(request, "Please fill in all required fields.")
            return render(request, self.template_name)
            
        try:
            # Save Barangay Info
            # Singleton: Get existing or create new
            info = BarangayInfo.objects.first()
            if not info:
                info = BarangayInfo()
                
            info.name = name
            info.street = street
            info.city_municipality = city_municipality
            info.province = province
            info.region = region
            info.zip_code = zip_code
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

            # Auto-create / update the Barangay Hall blip
            try:
                from apps.gis.models import EmergencyService
                hall_address = info.full_address or f"{info.street}, {info.city_municipality}, {info.province}".strip(', ')
                defaults = {
                    'name': f"{info.name} — Barangay Hall",
                    'address': hall_address,
                    'contact_number': info.contact_number or '',
                    'description': f"Official Barangay Hall of {info.name}.",
                    'icon_emoji': '🏛️',
                    'is_active': True,
                }
                if info.latitude and info.longitude:
                    defaults['latitude'] = info.latitude
                    defaults['longitude'] = info.longitude
                EmergencyService.objects.update_or_create(
                    service_type='hall',
                    defaults=defaults,
                )
            except Exception as _hall_err:
                pass  # Non-fatal; don't block setup completion

            # Save Puroks
            from apps.residents.models import Purok
            purok_names = request.POST.getlist('puroks[]')
            # Clear existing if any (since this is setup, usually empty)
            for p_name in purok_names:
                if p_name.strip():
                    Purok.objects.get_or_create(name=p_name.strip())
            
            # Create/Update Admin User
            # ... existing admin logic ...
            if User.objects.filter(username=username).exists():
                user = User.objects.get(username=username)
                user.set_password(password)
                # user.email = admin_email 
                user.role = 'admin'
                user.is_superuser = True
                user.is_staff = True
                user.is_bootstrap = True # Set is_bootstrap to True
                user.save()
            else:
                User.objects.create_superuser(
                    username=username,
                    # email=admin_email,
                    email='',
                    password=password,
                    role='admin',
                    barangay_position='Administrator',
                    is_bootstrap=True # Set is_bootstrap to True
                )
                
            messages.success(request, "System Setup Completed Successfully! Initializing your workspace...")
            return redirect('core:initializing')
            
        except Exception as e:
            messages.error(request, f"An error occurred: {str(e)}")
            return render(request, self.template_name)

class InitializingView(TemplateView):
    """Premium loading screen for system initialization"""
    template_name = 'core/initializing.html'

@method_decorator(role_required(['admin']), name='dispatch')
class TriggerInitializeAPI(LoginRequiredMixin, View):
    """API endpoint to trigger background initialization tasks (like GIS import)"""
    def post(self, request):
        from django.core.management import call_command
        from django.http import JsonResponse
        import threading

        def run_initialization():
            try:
                # Trigger the GIS Importer
                # Note: Radius is set to 5km by default
                call_command('import_nearby_services', radius=5000)
            except Exception as e:
                print(f"Initialization background task error: {e}")

        # Run in background thread to avoid blocking the UI
        thread = threading.Thread(target=run_initialization)
        thread.daemon = True
        thread.start()

        return JsonResponse({'status': 'started', 'message': 'Initialization background tasks triggered.'})

# ── Officials ──────────────────────────────────────────────────────────────

from django.views.generic import ListView, CreateView, UpdateView
from django.contrib.auth.mixins import LoginRequiredMixin
from apps.core.models import BarangayOfficial


class OfficialsListView(LoginRequiredMixin, ListView):
    model = BarangayOfficial
    template_name = 'pages/officials/list.html'
    context_object_name = 'officials'

    def get_queryset(self):
        return BarangayOfficial.objects.all()


@method_decorator(role_required(['admin']), name='dispatch')
class OfficialCreateView(LoginRequiredMixin, View):
    template_name = 'pages/officials/form.html'

    def get(self, request):
        from apps.core.models import BarangayOfficial as BOf
        return render(request, self.template_name, {
            'position_choices': BOf.POSITION_CHOICES,
            'committee_choices': BOf.COMMITTEE_CHOICES,
            'action': 'Add',
        })

    def post(self, request):
        from apps.core.models import BarangayOfficial as BOf
        try:
            official = BOf()
            official.position = request.POST.get('position')
            official.committee = request.POST.get('committee', '')
            official.honorific = request.POST.get('honorific', '')
            official.first_name = request.POST.get('first_name')
            official.middle_name = request.POST.get('middle_name', '')
            official.last_name = request.POST.get('last_name')
            official.suffix = request.POST.get('suffix', '')
            if request.FILES.get('photo'):
                official.photo = request.FILES['photo']
            official.term_start = request.POST.get('term_start') or None
            official.term_end = request.POST.get('term_end') or None
            official.contact_number = request.POST.get('contact_number', '')
            official.email = request.POST.get('email', '')
            official.is_active = request.POST.get('is_active') == 'on'
            official.order = int(request.POST.get('order', 0))
            official.save()

            # If this is Punong Barangay, update captain_name on BarangayInfo
            if official.position == 'punong_barangay':
                from apps.core.models import BarangayInfo
                info = BarangayInfo.objects.first()
                if info:
                    info.captain_name = official.display_name.upper()
                    info.save(update_fields=['captain_name'])

            messages.success(request, f"{official.full_name} has been added.")
            return redirect('core:officials')
        except Exception as e:
            messages.error(request, f"Error: {str(e)}")
            return render(request, self.template_name, {
                'position_choices': BOf.POSITION_CHOICES,
                'committee_choices': BOf.COMMITTEE_CHOICES,
                'action': 'Add',
            })


@method_decorator(role_required(['admin']), name='dispatch')
class OfficialUpdateView(LoginRequiredMixin, View):
    template_name = 'pages/officials/form.html'

    def get(self, request, pk):
        from django.shortcuts import get_object_or_404
        from apps.core.models import BarangayOfficial as BOf
        official = get_object_or_404(BOf, pk=pk)
        return render(request, self.template_name, {
            'official': official,
            'position_choices': BOf.POSITION_CHOICES,
            'committee_choices': BOf.COMMITTEE_CHOICES,
            'action': 'Edit',
        })

    def post(self, request, pk):
        from django.shortcuts import get_object_or_404
        from apps.core.models import BarangayOfficial as BOf
        official = get_object_or_404(BOf, pk=pk)
        try:
            official.position = request.POST.get('position')
            official.committee = request.POST.get('committee', '')
            official.honorific = request.POST.get('honorific', '')
            official.first_name = request.POST.get('first_name')
            official.middle_name = request.POST.get('middle_name', '')
            official.last_name = request.POST.get('last_name')
            official.suffix = request.POST.get('suffix', '')
            if request.FILES.get('photo'):
                official.photo = request.FILES['photo']
            official.term_start = request.POST.get('term_start') or None
            official.term_end = request.POST.get('term_end') or None
            official.contact_number = request.POST.get('contact_number', '')
            official.email = request.POST.get('email', '')
            official.is_active = request.POST.get('is_active') == 'on'
            official.order = int(request.POST.get('order', 0))
            official.save()

            if official.position == 'punong_barangay':
                from apps.core.models import BarangayInfo
                info = BarangayInfo.objects.first()
                if info:
                    info.captain_name = official.display_name.upper()
                    info.save(update_fields=['captain_name'])

            messages.success(request, f"{official.full_name} has been updated.")
            return redirect('core:officials')
        except Exception as e:
            messages.error(request, f"Error: {str(e)}")
            return render(request, self.template_name, {
                'official': official,
                'position_choices': BOf.POSITION_CHOICES,
                'committee_choices': BOf.COMMITTEE_CHOICES,
                'action': 'Edit',
            })


@method_decorator(role_required(['admin']), name='dispatch')
class OfficialDeleteView(LoginRequiredMixin, View):
    def post(self, request, pk):
        from django.shortcuts import get_object_or_404
        official = get_object_or_404(BarangayOfficial, pk=pk)
        name = official.full_name
        official.delete()
        messages.success(request, f"{name} has been removed.")
        return redirect('core:officials')

# ── Informational Pages ──────────────────────────────────────────────────

class AboutView(LoginRequiredMixin, TemplateView):
    template_name = 'pages/info/about.html'

class PrivacyView(LoginRequiredMixin, TemplateView):
    template_name = 'pages/info/privacy.html'

class TermsView(LoginRequiredMixin, TemplateView):
    template_name = 'pages/info/terms.html'

class ProfileView(LoginRequiredMixin, View):
    template_name = 'core/profile.html'
    
    def get(self, request):
        return render(request, self.template_name)
        
    def post(self, request):
        user = request.user
        first_name = request.POST.get('first_name')
        last_name = request.POST.get('last_name')
        email = request.POST.get('email')
        
        try:
            user.first_name = first_name
            user.last_name = last_name
            user.email = email
            user.save()
            messages.success(request, "Profile updated successfully.")
        except Exception as e:
            messages.error(request, f"Error updating profile: {str(e)}")
            
        return redirect('core:profile')

class MarkNotificationReadView(LoginRequiredMixin, View):
    def post(self, request, pk):
        from django.shortcuts import get_object_or_404
        notification = get_object_or_404(Notification, pk=pk, user=request.user)
        notification.is_read = True
        notification.save()
        
        # Return an empty response for HTMX (the item will be removed/updated in the UI)
        return HttpResponse("")
# Error Views
def error_404(request, exception):
    return render(request, '404.html', status=404)

def error_500(request):
    import logging
    logger = logging.getLogger('apps')
    logger.exception("An unhandled 500 error occurred.")
    return render(request, '500.html', status=500)
