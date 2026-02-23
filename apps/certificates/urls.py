from django.urls import path
from . import views

app_name = 'certificates'

urlpatterns = [
    path('', views.CertificateCenterView.as_view(), name='center'),
    path('list/', views.CertificateListView.as_view(), name='list'),
    path('<int:pk>/print/', views.CertificatePrintView.as_view(), name='print'),
    path('<int:pk>/void/', views.void_certificate, name='void'),
]
