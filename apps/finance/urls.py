from django.urls import path
from . import views

app_name = 'finance'

urlpatterns = [
    path('', views.FinanceDashboardView.as_view(), name='dashboard'),
    path('receipts/', views.OfficialReceiptListView.as_view(), name='receipt_list'),
]
