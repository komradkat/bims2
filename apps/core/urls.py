# Core URLs
from django.urls import path
from django.views.generic import TemplateView
from django.contrib.auth.views import LogoutView
from . import views

app_name = 'core'

urlpatterns = [
    path('login/', views.CustomLoginView.as_view(), name='login'),
    path('logout/', LogoutView.as_view(next_page='core:login'), name='logout'),
    
    # License Management
    path('license/activate/', views.LicenseActivationView.as_view(), name='license_activation'),
    
    # User Management
    path('users/', views.UserListView.as_view(), name='user_list'),
    path('users/add/', views.UserCreateView.as_view(), name='user_add'),
    path('users/<int:pk>/edit/', views.UserUpdateView.as_view(), name='user_edit'),
    # Dashboard
    path('', views.DashboardView.as_view(), name='dashboard'),
    
    # Residents
    path('residents/', views.ResidentsListView.as_view(), name='residents_list'),
    path('residents/add/', TemplateView.as_view(template_name='pages/residents/form.html'), name='residents_add'),
    path('certificates/', TemplateView.as_view(template_name='pages/certificates/center.html'), name='certificates'),
    path('business/', views.BusinessListView.as_view(), name='business_list'),
    path('business/add/', TemplateView.as_view(template_name='pages/business/form.html'), name='business_add'),
    path('blotter/', views.BlotterListView.as_view(), name='blotter_list'),
    path('blotter/add/', TemplateView.as_view(template_name='pages/blotter/form.html'), name='blotter_add'),
    path('finance/', views.FinanceDashboardView.as_view(), name='finance'),
    path('audit-logs/', views.AuditLogsView.as_view(), name='audit_logs'),
    path('gis-map/', views.GisMapView.as_view(), name='gis_map'),
]

