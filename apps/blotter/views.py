from django.shortcuts import redirect
from django.views.generic import ListView, CreateView, DetailView, View
from django.contrib.auth.mixins import LoginRequiredMixin
from apps.core.mixins import NonBootstrapRequiredMixin
from django.urls import reverse_lazy
from django.db.models import Q
from django.utils import timezone
from django.contrib import messages
from .models import BlotterCase, Complainant, Respondent, Hearing
from .forms import BlotterCaseForm, ComplainantForm, RespondentForm, HearingForm


class BlotterListView(LoginRequiredMixin, NonBootstrapRequiredMixin, ListView):
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


class BlotterCreateView(LoginRequiredMixin, NonBootstrapRequiredMixin, CreateView):
    model = BlotterCase
    form_class = BlotterCaseForm
    template_name = 'pages/blotter/form.html'
    success_url = reverse_lazy('blotter:list')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        if self.request.POST:
            context['complainant_form'] = ComplainantForm(self.request.POST, prefix='complainant')
            context['respondent_form'] = RespondentForm(self.request.POST, prefix='respondent')
            context['hearing_form'] = HearingForm(self.request.POST, prefix='hearing')
        else:
            context['complainant_form'] = ComplainantForm(prefix='complainant')
            context['respondent_form'] = RespondentForm(prefix='respondent')
            context['hearing_form'] = HearingForm(prefix='hearing')
        return context

    def form_valid(self, form):
        context = self.get_context_data()
        complainant_form = context['complainant_form']
        respondent_form = context['respondent_form']
        hearing_form = context['hearing_form']

        if complainant_form.is_valid() and respondent_form.is_valid():
            # Process BlotterCase
            nature = form.cleaned_data.get('nature_of_complaint')
            incident_dt = form.cleaned_data.get('incident_datetime')
            
            self.object = form.save(commit=False)
            self.object.incident_date = incident_dt
            self.object.narrative = f"Nature: {nature}\n\n{self.object.narrative}"
            self.object.created_by = self.request.user
            self.object.save()

            # Process Complainant
            complainant = complainant_form.save(commit=False)
            complainant.case = self.object
            complainant.save()

            # Process Respondent
            respondent = respondent_form.save(commit=False)
            respondent.case = self.object
            respondent.save()

            # Process Optional Hearing
            if hearing_form.is_valid() and hearing_form.cleaned_data.get('scheduled_at'):
                hearing = hearing_form.save(commit=False)
                hearing.case = self.object
                hearing.save()
            
            messages.success(self.request, f"New blotter case {self.object.case_number} has been recorded.")
            return redirect(self.success_url)
        else:
            return self.render_to_response(self.get_context_data(form=form))



class BlotterDetailView(LoginRequiredMixin, NonBootstrapRequiredMixin, DetailView):
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


class HearingCreateView(LoginRequiredMixin, NonBootstrapRequiredMixin, CreateView):
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


class CaseStatusUpdateView(LoginRequiredMixin, NonBootstrapRequiredMixin, View):
    def post(self, request, pk):
        case = BlotterCase.objects.get(pk=pk)
        new_status = request.POST.get('status')
        if new_status in dict(BlotterCase.STATUS_CHOICES):
            case.status = new_status
            case.save()
            messages.success(request, f"Case {case.case_number} status updated to {case.get_status_display()}.")
        return redirect('blotter:detail', pk=pk)
