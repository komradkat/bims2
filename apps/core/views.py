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

