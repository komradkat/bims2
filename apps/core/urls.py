# Core URLs
from django.urls import path
from django.contrib.auth.views import LogoutView
from . import views

app_name = 'core'

urlpatterns = [
    path('login/', views.CustomLoginView.as_view(), name='login'),
    path('logout/', LogoutView.as_view(next_page='core:login'), name='logout'),
    path('setup/', views.SetupView.as_view(), name='setup'),
    
    # License Management
    path('license/activate/', views.LicenseActivationView.as_view(), name='license_activation'),
    
    # User Management
    path('users/', views.UserListView.as_view(), name='user_list'),
    path('users/add/', views.UserCreateView.as_view(), name='user_add'),
    path('users/<int:pk>/edit/', views.UserUpdateView.as_view(), name='user_edit'),
    # Dashboard
    path('', views.DashboardView.as_view(), name='dashboard'),

    # Officials
    path('officials/', views.OfficialsListView.as_view(), name='officials'),
    path('officials/add/', views.OfficialCreateView.as_view(), name='official_add'),
    path('officials/<int:pk>/edit/', views.OfficialUpdateView.as_view(), name='official_edit'),
    path('officials/<int:pk>/delete/', views.OfficialDeleteView.as_view(), name='official_delete'),

    # GIS Map (Ultra only)
    path('gis-map/', views.GisMapView.as_view(), name='gis_map'),
]
