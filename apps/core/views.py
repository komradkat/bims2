# Core views
from django.shortcuts import render
from django.views.generic import TemplateView


class DashboardView(TemplateView):
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


class BlotterListView(TemplateView):
    """Blotter list view with placeholder data"""
    template_name = 'pages/blotter/list.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        # Statistics data
        context['stats'] = {
            'total_cases': 15,
            'active_cases': 4,
            'settled_cases': 8,
            'urgent_hearings': 1,
        }
        
        # Placeholder blotter cases data
        context['cases'] = [
            {
                'case_number': '2026-003',
                'parties': 'Jose Ryan vs. Cardo Dalisay',
                'description': 'Property Boundary Dispute',
                'type': 'Civil',
                'status': 'Mediation',
                'status_color': 'warning',
                'hearing_date': 'Tomorrow, 2:00 PM',
                'hearing_class': 'text-error font-medium',
                'action_button': 'Update',
                'opacity': '',
            },
            {
                'case_number': '2026-004',
                'parties': 'Marites Chismosa vs. Barangay',
                'description': 'Unjust Vexation',
                'type': 'Criminal',
                'status': 'Conciliation',
                'status_color': 'info',
                'hearing_date': 'Jan 26, 2026',
                'hearing_class': '',
                'action_button': 'Update',
                'opacity': '',
            },
            {
                'case_number': '2026-001',
                'parties': 'Tito Sotto vs. Vic Sotto',
                'description': 'Collection of Sum of Money',
                'type': 'Civil',
                'status': 'Settled',
                'status_color': 'success',
                'hearing_date': '--',
                'hearing_class': '',
                'action_button': 'View',
                'opacity': 'opacity-50',
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
