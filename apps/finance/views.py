from django.views.generic import TemplateView, ListView
from django.contrib.auth.mixins import LoginRequiredMixin
from apps.core.mixins import NonBootstrapRequiredMixin
from django.db.models import Sum, Count
from django.db.models.functions import TruncMonth
from django.utils import timezone
from django.utils.decorators import method_decorator
from django.contrib import messages
from datetime import timedelta

from apps.core.decorators import tier_required
from .models import OfficialReceipt

@method_decorator(tier_required(['pro', 'ultra']), name='dispatch')
class FinanceDashboardView(LoginRequiredMixin, NonBootstrapRequiredMixin, TemplateView):
    template_name = 'pages/finance/dashboard.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        now = timezone.now()
        today = now.date()
        month_start = today.replace(day=1)

        # Statistics data
        daily_collection = OfficialReceipt.objects.filter(
            date__date=today,
            status='paid'
        ).aggregate(Sum('amount'))['amount__sum'] or 0

        monthly_revenue = OfficialReceipt.objects.filter(
            date__gte=month_start,
            status='paid'
        ).aggregate(Sum('amount'))['amount__sum'] or 0

        context['stats'] = {
            'daily_collection': daily_collection,
            'date_today': today.strftime('%b %d, %Y'),
            'monthly_revenue': monthly_revenue,
            'month_range': f"{month_start.strftime('%b 1')} - {today.strftime('%b %d')}",
        }

        # Recent receipts
        context['receipts'] = OfficialReceipt.objects.all().order_by('-date')[:20]

        return context

@method_decorator(tier_required(['ultra']), name='dispatch')
class RevenueAnalyticsView(LoginRequiredMixin, NonBootstrapRequiredMixin, TemplateView):
    template_name = 'pages/finance/analytics.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        # 1. Monthly Trends (Last 6 Months)
        six_months_ago = timezone.now() - timedelta(days=180)
        trends = OfficialReceipt.objects.filter(
            date__gte=six_months_ago,
            status='paid'
        ).annotate(
            month=TruncMonth('date')
        ).values('month').annotate(
            total=Sum('amount'),
            count=Count('id')
        ).order_by('month')

        # 2. Revenue by Particulars (Pie Chart data)
        source_breakdown = OfficialReceipt.objects.filter(
            status='paid'
        ).values('particulars').annotate(
            total=Sum('amount')
        ).order_by('-total')[:10]

        total_all_time = OfficialReceipt.objects.filter(status='paid').aggregate(Sum('amount'))['amount__sum'] or 0
        count_all_time = OfficialReceipt.objects.filter(status='paid').count()
        avg_per_receipt = total_all_time / count_all_time if count_all_time > 0 else 0

        context.update({
            'trends': trends,
            'source_breakdown': source_breakdown,
            'total_all_time': total_all_time,
            'count_all_time': count_all_time,
            'avg_per_receipt': avg_per_receipt,
        })
        return context

@method_decorator(tier_required(['pro', 'ultra']), name='dispatch')
class OfficialReceiptListView(LoginRequiredMixin, NonBootstrapRequiredMixin, ListView):
    model = OfficialReceipt
    template_name = 'pages/finance/list.html'
    context_object_name = 'receipts'
    paginate_by = 50

    def get_queryset(self):
        return OfficialReceipt.objects.all().order_by('-date')
