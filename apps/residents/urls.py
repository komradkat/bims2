# Residents URLs
from django.urls import path
from . import views

app_name = 'residents'

urlpatterns = [
    path('', views.ResidentsListView.as_view(), name='list'),
    path('add/', views.ResidentCreateView.as_view(), name='add'),
    path('<int:pk>/', views.ResidentDetailView.as_view(), name='detail'),
    path('<int:pk>/edit/', views.ResidentUpdateView.as_view(), name='edit'),
    path('export/', views.export_residents_excel, name='export_excel'),
]
