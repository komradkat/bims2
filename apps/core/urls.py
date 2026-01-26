# Core URLs
from django.urls import path
from . import views

app_name = 'core'

urlpatterns = [
    # Dashboard
    path('', views.DashboardView.as_view(), name='dashboard'),
    
    # Residents
    path('residents/', views.ResidentsListView.as_view(), name='residents_list'),
    path('residents/add/', views.DashboardView.as_view(), name='residents_add'),
    path('certificates/', views.DashboardView.as_view(), name='certificates'),
    path('business/', views.DashboardView.as_view(), name='business_list'),
    path('blotter/', views.DashboardView.as_view(), name='blotter_list'),
    path('finance/', views.DashboardView.as_view(), name='finance'),
    path('audit-logs/', views.DashboardView.as_view(), name='audit_logs'),
    path('gis-map/', views.DashboardView.as_view(), name='gis_map'),
]

