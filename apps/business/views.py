from django.views.generic import ListView, CreateView, UpdateView
from django.contrib.auth.mixins import LoginRequiredMixin
from apps.core.mixins import NonBootstrapRequiredMixin
from django.db.models import Sum, Q
from django.urls import reverse_lazy
from django.utils import timezone
from .models import BusinessPermit, BusinessClearance
from .forms import BusinessPermitForm
from django.contrib import messages


from django.utils.decorators import method_decorator


class BusinessListView(LoginRequiredMixin, NonBootstrapRequiredMixin, ListView):
    model = BusinessPermit
    template_name = "pages/business/list.html"
    context_object_name = "businesses"
    paginate_by = 20

    def get_queryset(self):
        queryset = BusinessPermit.objects.all()

        # Search functionality
        search_query = self.request.GET.get("search", "").strip()
        if search_query:
            queryset = queryset.filter(
                Q(business_name__icontains=search_query)
                | Q(owner_name__icontains=search_query)
                | Q(permit_number__icontains=search_query)
            )

        return queryset.order_by("-created_at")

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        # Statistics
        today = timezone.now().date()
        context["stats"] = {
            "active_permits": BusinessPermit.objects.filter(
                status="active", expiration_date__gte=today
            ).count(),
            "expired": BusinessPermit.objects.filter(expiration_date__lt=today).count(),
            "pending": BusinessPermit.objects.filter(status="pending").count(),
            "total_revenue": BusinessClearance.objects.aggregate(Sum("amount_paid"))[
                "amount_paid__sum"
            ]
            or 0,
        }

        return context


class BusinessCreateView(LoginRequiredMixin, NonBootstrapRequiredMixin, CreateView):
    model = BusinessPermit
    form_class = BusinessPermitForm
    template_name = "pages/business/form.html"
    success_url = reverse_lazy("business:list")

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["action"] = "Add"
        context["title"] = "New Business Permit"
        return context

    def form_valid(self, form):
        form.instance.created_by = self.request.user
        if not form.instance.status:
            form.instance.status = "active"

        # Save the permit
        response = super().form_valid(form)

        # Create a clearance record if fee is paid
        if form.instance.clearance_fee > 0:
            BusinessClearance.objects.create(
                permit=self.object,
                or_number=form.instance.or_number,
                amount_paid=form.instance.clearance_fee,
                issued_by=self.request.user,
            )

        messages.success(
            self.request,
            f"Business Permit for {form.instance.business_name} created successfully.",
        )
        return response


class BusinessUpdateView(LoginRequiredMixin, NonBootstrapRequiredMixin, UpdateView):
    model = BusinessPermit
    form_class = BusinessPermitForm
    template_name = "pages/business/form.html"
    success_url = reverse_lazy("business:list")

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["action"] = "Edit"
        context["title"] = "Edit Business Permit"
        return context

    def form_valid(self, form):
        response = super().form_valid(form)
        messages.success(
            self.request,
            f"Business Permit for {form.instance.business_name} updated successfully.",
        )
        return response
