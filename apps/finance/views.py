from django.views.generic import TemplateView, ListView
from django.contrib.auth.mixins import LoginRequiredMixin
from apps.core.mixins import NonBootstrapRequiredMixin
from django.db.models import Sum
from django.utils import timezone
from .models import OfficialReceipt

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

class OfficialReceiptListView(LoginRequiredMixin, NonBootstrapRequiredMixin, ListView):
    model = OfficialReceipt
    template_name = 'pages/finance/list.html' # Need to check if this template exists or if I should reuse dashboard
    context_object_name = 'receipts'
    paginate_by = 50

    def get_queryset(self):
        return OfficialReceipt.objects.all().order_by('-date')
