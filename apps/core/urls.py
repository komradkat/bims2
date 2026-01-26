# Core URLs
from django.urls import path
from django.views.generic import TemplateView
from . import views

app_name = 'core'

urlpatterns = [
    # Dashboard
    path('', views.DashboardView.as_view(), name='dashboard'),
    
    # Residents
    path('residents/', views.ResidentsListView.as_view(), name='residents_list'),
    path('residents/add/', TemplateView.as_view(template_name='pages/residents/form.html'), name='residents_add'),
    path('certificates/', TemplateView.as_view(template_name='pages/certificates/center.html'), name='certificates'),
    path('business/', views.DashboardView.as_view(), name='business_list'),
    path('blotter/', views.BlotterListView.as_view(), name='blotter_list'),
    path('blotter/add/', TemplateView.as_view(template_name='pages/blotter/form.html'), name='blotter_add'),
    path('finance/', views.DashboardView.as_view(), name='finance'),
    path('audit-logs/', views.DashboardView.as_view(), name='audit_logs'),
    path('gis-map/', views.DashboardView.as_view(), name='gis_map'),
]

