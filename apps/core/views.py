# Core views
from django.shortcuts import render, redirect
from django.views.generic import TemplateView, View
from django.contrib.auth.views import LoginView
from django.urls import reverse_lazy
from django.contrib import messages
from django.core.cache import cache



class CustomLoginView(LoginView):
    template_name = 'auth/login.html'
    redirect_authenticated_user = True
    
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
    """Dashboard view with placeholder data"""
    template_name = 'pages/dashboard.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # Placeholder data for testing
        context['stats'] = {
            'total_residents': 1204,
            'documents_issued': 89,
            'total_revenue': 45000,
            'active_cases': 3,
        }
        
        # Recent Certificates data
        context['recent_certificates'] = [
            {
                'recipient': 'Maria dela Cruz',
                'type': 'Indigency',
                'date': 'Today, 10:42 AM',
                'status': 'Issued',
            },
            {
                'recipient': 'Juan Santos',
                'type': 'Barangay Clearance',
                'date': 'Today, 09:15 AM',
                'status': 'Issued',
            },
            {
                'recipient': 'Pedro Penduko',
                'type': 'Residency',
                'date': 'Yesterday',
                'status': 'Issued',
            },
        ]
        
        # Urgent Blotter Cases data
        context['urgent_cases'] = [
            {
                'priority_number': '1',
                'priority_color': 'error',
                'title': 'Case #2026-003',
                'description': 'Boundary Dispute - Sitio 1',
                'schedule': 'Hearing: Tomorrow 2PM',
            },
            {
                'priority_number': '2',
                'priority_color': 'warning',
                'title': 'Case #2026-004',
                'description': 'Complaint vs. Animal Control',
                'schedule': 'Mediation: Jan 28',
            },
        ]
        
        # Data for activity table
        context['activity_headers'] = ['Time', 'Activity', 'User', 'Status']
        context['activity_rows'] = [
            {
                'cells': [
                    '10:30 AM',
                    'Certificate of Indigency issued to Juan Dela Cruz',
                    'Admin User',
                    '<span class="badge badge-success">Completed</span>',
                ]
            },
            {
                'cells': [
                    '10:15 AM',
                    'New resident registered: Maria Santos',
                    'Admin User',
                    '<span class="badge badge-success">Completed</span>',
                ]
            },
            {
                'cells': [
                    '9:45 AM',
                    'Business permit renewed: Sari-Sari Store',
                    'Admin User',
                    '<span class="badge badge-success">Completed</span>',
                ]
            },
        ]
        
        return context




class ResidentsListView(TemplateView):
    """Residents list view with placeholder data"""
    template_name = 'pages/residents/list.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        # Placeholder resident data
        context['residents'] = [
            {
                'name': 'Juan Dela Cruz',
                'id': 'BID-2026-001',
                'age': 45,
                'sex': 'M',
                'civil_status': 'Married',
                'address': '123 Kalye Serye, Purok 1',
                'sectors': [
                    {'name': 'Indigent', 'color': 'error'},
                ],
            },
            {
                'name': 'Maria Santos',
                'id': 'BID-2026-005',
                'age': 68,
                'sex': 'F',
                'civil_status': 'Widowed',
                'address': '45 Mabini St, Purok 2',
                'sectors': [
                    {'name': 'Senior Citizen', 'color': 'info'},
                ],
            },
            {
                'name': 'Pedro Penduko',
                'id': 'BID-2026-012',
                'age': 32,
                'sex': 'M',
                'civil_status': 'Single',
                'address': '78 Rizal Ave, Purok 1',
                'sectors': [
                    {'name': '4Ps', 'color': 'warning'},
                    {'name': 'Solo Parent', 'color': 'secondary'},
                ],
            },
            {
                'name': 'Ana Reyes',
                'id': 'BID-2026-018',
                'age': 29,
                'sex': 'F',
                'civil_status': 'Married',
                'address': '56 Luna St, Purok 3',
                'sectors': [
                    {'name': 'PWD', 'color': 'accent'},
                ],
            },
            {
                'name': 'Roberto Garcia',
                'id': 'BID-2026-023',
                'age': 52,
                'sex': 'M',
                'civil_status': 'Married',
                'address': '89 Bonifacio Rd, Purok 2',
                'sectors': [],
            },
            {
                'name': 'Linda Mercado',
                'id': 'BID-2026-027',
                'age': 71,
                'sex': 'F',
                'civil_status': 'Widowed',
                'address': '12 Aguinaldo St, Purok 1',
                'sectors': [
                    {'name': 'Senior Citizen', 'color': 'info'},
                    {'name': 'Indigent', 'color': 'error'},
                ],
            },
            {
                'name': 'Carlos Ramos',
                'id': 'BID-2026-031',
                'age': 38,
                'sex': 'M',
                'civil_status': 'Married',
                'address': '34 Del Pilar Ave, Purok 3',
                'sectors': [
                    {'name': '4Ps', 'color': 'warning'},
                ],
            },
            {
                'name': 'Elena Cruz',
                'id': 'BID-2026-035',
                'age': 26,
                'sex': 'F',
                'civil_status': 'Single',
                'address': '67 Quezon Blvd, Purok 2',
                'sectors': [],
            },
            {
                'name': 'Fernando Lopez',
                'id': 'BID-2026-042',
                'age': 55,
                'sex': 'M',
                'civil_status': 'Married',
                'address': '90 Roxas St, Purok 1',
                'sectors': [
                    {'name': 'PWD', 'color': 'accent'},
                ],
            },
            {
                'name': 'Gloria Tan',
                'id': 'BID-2026-048',
                'age': 42,
                'sex': 'F',
                'civil_status': 'Separated',
                'address': '23 Magsaysay Ave, Purok 3',
                'sectors': [
                    {'name': 'Solo Parent', 'color': 'secondary'},
                    {'name': '4Ps', 'color': 'warning'},
                ],
            },
            {
                'name': 'Henry Villanueva',
                'id': 'BID-2026-053',
                'age': 60,
                'sex': 'M',
                'civil_status': 'Married',
                'address': '45 Osmena Rd, Purok 2',
                'sectors': [],
            },
            {
                'name': 'Isabel Flores',
                'id': 'BID-2026-059',
                'age': 34,
                'sex': 'F',
                'civil_status': 'Married',
                'address': '78 Laurel St, Purok 1',
                'sectors': [
                    {'name': 'Indigent', 'color': 'error'},
                ],
            },
            {
                'name': 'Jose Bautista',
                'id': 'BID-2026-064',
                'age': 73,
                'sex': 'M',
                'civil_status': 'Married',
                'address': '12 Quirino Ave, Purok 3',
                'sectors': [
                    {'name': 'Senior Citizen', 'color': 'info'},
                ],
            },
            {
                'name': 'Karen Diaz',
                'id': 'BID-2026-070',
                'age': 28,
                'sex': 'F',
                'civil_status': 'Single',
                'address': '56 Macapagal Blvd, Purok 2',
                'sectors': [
                    {'name': 'PWD', 'color': 'accent'},
                    {'name': '4Ps', 'color': 'warning'},
                ],
            },
            {
                'name': 'Luis Mendoza',
                'id': 'BID-2026-075',
                'age': 49,
                'sex': 'M',
                'civil_status': 'Married',
                'address': '89 Ramos St, Purok 1',
                'sectors': [],
            },
            {
                'name': 'Maricel Aquino',
                'id': 'BID-2026-081',
                'age': 36,
                'sex': 'F',
                'civil_status': 'Married',
                'address': '23 Burgos Ave, Purok 2',
                'sectors': [
                    {'name': '4Ps', 'color': 'warning'},
                ],
            },
            {
                'name': 'Nelson Soriano',
                'id': 'BID-2026-087',
                'age': 67,
                'sex': 'M',
                'civil_status': 'Married',
                'address': '45 Jacinto St, Purok 3',
                'sectors': [
                    {'name': 'Senior Citizen', 'color': 'info'},
                ],
            },
            {
                'name': 'Olivia Pascual',
                'id': 'BID-2026-092',
                'age': 31,
                'sex': 'F',
                'civil_status': 'Single',
                'address': '67 Gomez Rd, Purok 1',
                'sectors': [
                    {'name': 'Solo Parent', 'color': 'secondary'},
                ],
            },
            {
                'name': 'Pablo Navarro',
                'id': 'BID-2026-098',
                'age': 44,
                'sex': 'M',
                'civil_status': 'Married',
                'address': '12 Zamora Blvd, Purok 2',
                'sectors': [],
            },
            {
                'name': 'Queenie Salazar',
                'id': 'BID-2026-104',
                'age': 58,
                'sex': 'F',
                'civil_status': 'Widowed',
                'address': '34 Paterno Ave, Purok 3',
                'sectors': [
                    {'name': 'Indigent', 'color': 'error'},
                ],
            },
        ]
        
        return context


class BusinessListView(TemplateView):
    """Business permits list view with placeholder data"""
    template_name = 'pages/business/list.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        # Statistics data
        context['stats'] = {
            'active_permits': 245,
            'expired': 12,
            'pending': 8,
            'total_revenue': '125k',
        }
        
        # Placeholder business permits data
        context['businesses'] = [
            {
                'name': "Aling Nena's Sari-Sari Store",
                'owner': 'Nena Magalona',
                'permit_number': 'BP-2025-001',
                'expiration': 'Dec 31, 2025',
                'expiration_class': '',
                'status': 'Active',
                'status_color': 'success',
            },
            {
                'name': 'Mang Inasal 2',
                'owner': 'Edgar Sia II',
                'permit_number': 'BP-2025-042',
                'expiration': 'Dec 31, 2025',
                'expiration_class': '',
                'status': 'Active',
                'status_color': 'success',
            },
            {
                'name': 'Computer Shop 143',
                'owner': 'Mark Zuckerberg',
                'permit_number': 'BP-2024-112',
                'expiration': 'Dec 31, 2024',
                'expiration_class': 'text-error font-semibold',
                'status': 'Expired',
                'status_color': 'error',
            },
        ]
        
        return context


@method_decorator(tier_required(['pro', 'ultra']), name='dispatch')
class FinanceDashboardView(TemplateView):
    """Finance dashboard view with placeholder data (Pro/Ultra only)"""
    template_name = 'pages/finance/dashboard.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        # Statistics data
        context['stats'] = {
            'daily_collection': '3,450',
            'date_today': 'Jan 24, 2026',
            'monthly_revenue': '45,200',
            'month_range': 'Jan 1 - Jan 24',
        }
        
        # Placeholder official receipts data
        context['receipts'] = [
            {
                'or_number': '7583921',
                'date': 'Jan 24, 2026',
                'payor': "Aling Nena's Store",
                'particulars': 'Business Clearance',
                'amount': '500.00',
                'status': 'Paid',
            },
            {
                'or_number': '7583922',
                'date': 'Jan 24, 2026',
                'payor': 'Juan Dela Cruz',
                'particulars': 'Brgy. Clearance',
                'amount': '100.00',
                'status': 'Paid',
            },
            {
                'or_number': '7583923',
                'date': 'Jan 24, 2026',
                'payor': 'Maria Santos',
                'particulars': 'Residency',
                'amount': '50.00',
                'status': 'Paid',
            },
        ]
        
        return context


class AuditLogsView(TemplateView):
    """Audit logs view with placeholder data"""
    template_name = 'pages/audit/logs.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        # Placeholder audit logs data
        context['logs'] = [
            {
                'timestamp': 'Jan 24, 11:42 AM',
                'user': 'admin',
                'action': 'Create',
                'action_color': 'success',
                'module': 'Certificates',
                'details': 'Issued Clearance for Juan Santos',
            },
            {
                'timestamp': 'Jan 24, 10:15 AM',
                'user': 'treasurer',
                'action': 'Update',
                'action_color': 'info',
                'module': 'Finance',
                'details': 'Verified OR #7583921',
            },
            {
                'timestamp': 'Jan 24, 09:30 AM',
                'user': 'clerk1',
                'action': 'Create',
                'action_color': 'success',
                'module': 'Residents',
                'details': 'Added resident profile: Maria Santos',
            },
            {
                'timestamp': 'Jan 23, 04:55 PM',
                'user': 'admin',
                'action': 'Delete',
                'action_color': 'error',
                'module': 'Residents',
                'details': 'Removed duplicate entry for ID: 9921',
            },
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

