from django.shortcuts import render, redirect
from django.views.generic import ListView, CreateView, DetailView, UpdateView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.urls import reverse_lazy
from django.db.models import Q
from django.utils import timezone
from django.contrib import messages
from .models import BlotterCase, Complainant, Respondent, Hearing


class BlotterListView(LoginRequiredMixin, ListView):
    model = BlotterCase
    template_name = 'pages/blotter/list.html'
    context_object_name = 'cases'
    paginate_by = 20

    def get_queryset(self):
        queryset = BlotterCase.objects.all().prefetch_related('complainants', 'respondents', 'hearings')
        
        # Simple status filtering
        status = self.request.GET.get('status')
        if status and status != 'all':
            queryset = queryset.filter(status=status)
            
        # Search
        q = self.request.GET.get('q')
        if q:
            queryset = queryset.filter(
                Q(case_number__icontains=q) |
                Q(narrative__icontains=q) |
                Q(complainants__name__icontains=q) |
                Q(respondents__name__icontains=q) |
                Q(complainants__resident__first_name__icontains=q) |
                Q(complainants__resident__last_name__icontains=q) |
                Q(respondents__resident__first_name__icontains=q) |
                Q(respondents__resident__last_name__icontains=q)
            ).distinct()
            
        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'Blotter Management'
        
        # Live stats
        all_cases = BlotterCase.objects.all()
        context['stats'] = {
            'total_cases': all_cases.count(),
            'active_cases': all_cases.exclude(status__in=['settled', 'dismissed', 'cfa']).count(),
            'settled_cases': all_cases.filter(status='settled').count(),
            'urgent_hearings': Hearing.objects.filter(
                status='scheduled', 
                scheduled_at__date=timezone.now().date()
            ).count()
        }
        
        return context


class BlotterCreateView(LoginRequiredMixin, CreateView):
    model = BlotterCase
    template_name = 'pages/blotter/form.html'
    fields = ['incident_type', 'incident_date', 'incident_location', 'narrative', 'status']
    success_url = reverse_lazy('blotter:list')

    def post(self, request, *args, **kwargs):
        # Extract case data
        incident_datetime = request.POST.get('incident_datetime')
        incident_location = request.POST.get('location')
        nature_of_complaint = request.POST.get('nature_of_complaint')
        narrative = request.POST.get('narrative')
        action_taken = request.POST.get('action_taken', 'mediation').lower()
        
        # Map action_taken to status if necessary
        status_map = {
            'mediation': 'mediation',
            'conciliation': 'conciliation',
            'arbitration': 'arbitration',
            'referred to police': 'dismissed',
            'for investigation': 'mediation',
        }
        status = status_map.get(action_taken, 'mediation')

        # Create the Case
        case = BlotterCase.objects.create(
            incident_type='others', # Placeholder for now, could map from nature_of_complaint
            incident_date=incident_datetime,
            incident_location=incident_location,
            narrative=f"Nature: {nature_of_complaint}\n\n{narrative}",
            status=status,
            created_by=request.user
        )

        # Extract Complainant
        c_first = request.POST.get('complainant_first_name')
        c_middle = request.POST.get('complainant_middle_name', '')
        c_last = request.POST.get('complainant_last_name')
        c_address = request.POST.get('complainant_address')
        c_contact = request.POST.get('complainant_contact')
        
        Complainant.objects.create(
            case=case,
            name=f"{c_first} {c_middle} {c_last}".strip().replace("  ", " "),
            address=c_address,
            contact_number=c_contact
        )

        # Extract Respondent
        r_first = request.POST.get('respondent_first_name')
        r_middle = request.POST.get('respondent_middle_name', '')
        r_last = request.POST.get('respondent_last_name')
        r_address = request.POST.get('respondent_address')
        r_contact = request.POST.get('respondent_contact')
        
        Respondent.objects.create(
            case=case,
            name=f"{r_first} {r_middle} {r_last}".strip().replace("  ", " "),
            address=r_address,
            contact_number=r_contact
        )

        # Handle Optional Hearing
        hearing_datetime = request.POST.get('hearing_datetime')
        hearing_venue = request.POST.get('hearing_venue')
        
        if hearing_datetime:
            Hearing.objects.create(
                case=case,
                scheduled_at=hearing_datetime,
                remarks=f"Venue: {hearing_venue}" if hearing_venue else ""
            )



class BlotterDetailView(LoginRequiredMixin, DetailView):
    model = BlotterCase
    template_name = 'pages/blotter/detail.html'
    context_object_name = 'case'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['complainants'] = self.object.complainants.all()
        context['respondents'] = self.object.respondents.all()
        # Order hearings by date, newest first for the timeline
        context['hearings'] = self.object.hearings.all().order_by('-scheduled_at')
        return context


class HearingCreateView(LoginRequiredMixin, CreateView):
    model = Hearing
    fields = ['scheduled_at', 'remarks']
    
    def form_valid(self, form):
        case_id = self.kwargs.get('case_id')
        case = BlotterCase.objects.get(id=case_id)
        form.instance.case = case
        messages.success(self.request, f"New hearing scheduled for {case.case_number}.")
        return super().form_valid(form)
    
    def get_success_url(self):
        return reverse_lazy('blotter:detail', kwargs={'pk': self.kwargs.get('case_id')})


class CaseStatusUpdateView(LoginRequiredMixin, View):
    def post(self, request, pk):
        case = BlotterCase.objects.get(pk=pk)
        new_status = request.POST.get('status')
        if new_status in dict(BlotterCase.STATUS_CHOICES):
            case.status = new_status
            case.save()
            messages.success(request, f"Case {case.case_number} status updated to {case.get_status_display()}.")
        return redirect('blotter:detail', pk=pk)
