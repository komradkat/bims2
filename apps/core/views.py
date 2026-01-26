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
        return context

