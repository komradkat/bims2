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
            'total_residents': 1234,
            'documents_issued': 567,
            'total_revenue': 45000,
            'active_cases': 12,
        }
        
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

