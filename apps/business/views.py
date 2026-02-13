from django.shortcuts import render, redirect, get_object_or_404
from django.views.generic import ListView, CreateView, UpdateView, DetailView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.db.models import Sum, Q
from django.urls import reverse_lazy
from django.utils import timezone
from .models import BusinessPermit, BusinessClearance
from django.contrib import messages

class BusinessListView(LoginRequiredMixin, ListView):
    model = BusinessPermit
    template_name = 'pages/business/list.html'
    context_object_name = 'businesses'
    paginate_by = 20

    def get_queryset(self):
        queryset = BusinessPermit.objects.all()

        # Search functionality
        search_query = self.request.GET.get('search', '').strip()
        if search_query:
            queryset = queryset.filter(
                Q(business_name__icontains=search_query) |
                Q(owner_name__icontains=search_query) |
                Q(permit_number__icontains=search_query)
            )

        return queryset.order_by('-created_at')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        # Statistics
        today = timezone.now().date()
        context['stats'] = {
            'active_permits': BusinessPermit.objects.filter(status='active', expiration_date__gte=today).count(),
            'expired': BusinessPermit.objects.filter(expiration_date__lt=today).count(),
            'pending': BusinessPermit.objects.filter(status='pending').count(),
            'total_revenue': BusinessClearance.objects.aggregate(Sum('amount_paid'))['amount_paid__sum'] or 0,
        }

        return context

class BusinessCreateView(LoginRequiredMixin, CreateView):
    model = BusinessPermit
    template_name = 'pages/business/form.html'
    fields = [
        'business_name', 'owner_name', 'owner_address', 'address',
        'contact_number', 'email', 'dti_sec_number', 'tin',
        'nature_of_business', 'cedula_number', 'cedula_date',
        'gross_sales', 'clearance_fee', 'or_number'
    ]
    success_url = reverse_lazy('business:list')

    def form_valid(self, form):
        form.instance.created_by = self.request.user
        form.instance.status = 'active' # Default to active when creating through form?

        # Save the permit
        response = super().form_valid(form)

        # Create a clearance record if fee is paid
        if form.instance.clearance_fee > 0:
            BusinessClearance.objects.create(
                permit=self.object,
                or_number=form.instance.or_number,
                amount_paid=form.instance.clearance_fee,
                issued_by=self.request.user
            )

        messages.success(self.request, f"Business Permit for {form.instance.business_name} created successfully.")
        return response

class BusinessUpdateView(LoginRequiredMixin, UpdateView):
    model = BusinessPermit
    template_name = 'pages/business/form.html'
    fields = [
        'business_name', 'owner_name', 'owner_address', 'address',
        'contact_number', 'email', 'dti_sec_number', 'tin',
        'nature_of_business', 'cedula_number', 'cedula_date',
        'gross_sales', 'clearance_fee', 'or_number', 'status'
    ]
    success_url = reverse_lazy('business:list')

    def form_valid(self, form):
        response = super().form_valid(form)
        messages.success(self.request, f"Business Permit for {form.instance.business_name} updated successfully.")
        return response
