from django.views.generic import ListView
from django.contrib.auth.mixins import LoginRequiredMixin
from apps.core.mixins import NonBootstrapRequiredMixin
from django.apps import apps

from apps.core.decorators import tier_required
from django.utils.decorators import method_decorator

@method_decorator(tier_required(['pro', 'ultra']), name='dispatch')
class AuditLogsView(LoginRequiredMixin, NonBootstrapRequiredMixin, ListView):
    template_name = 'pages/audit/logs.html'
    context_object_name = 'logs'
    paginate_by = 50

    def get_queryset(self):
        from .models import SystemLog
        
        models_to_track = [
            ('residents', 'Resident', 'Residents'),
            ('certificates', 'Certificate', 'Certificates'),
            ('blotter', 'BlotterCase', 'Blotter'),
            ('business', 'BusinessPermit', 'Business'),
            ('finance', 'OfficialReceipt', 'Finance'),
        ]

        all_logs = []

        # 1. Fetch Model History (Granular changes)
        for app_label, model_name, module_name in models_to_track:
            try:
                model = apps.get_model(app_label, model_name)
                if hasattr(model, 'history'):
                    records = model.history.all().order_by('-history_date')[:50]
                    for record in records:
                        action_map = {'+': 'Create', '~': 'Update', '-': 'Delete'}
                        action = action_map.get(record.history_type, 'Unknown')
                        color_map = {'Create': 'success', 'Update': 'info', 'Delete': 'error'}
                        action_color = color_map.get(action, 'ghost')

                        details = f"{action} record: {str(record)}"
                        if record.history_change_reason:
                            details += f" ({record.history_change_reason})"

                        user_display = record.history_user.username if record.history_user else 'System'

                        all_logs.append({
                            'timestamp': record.history_date,
                            'user': user_display,
                            'action': action,
                            'action_color': action_color,
                            'module': module_name,
                            'details': details,
                            'is_system': False
                        })
            except LookupError:
                continue

        # 2. Fetch System Logs (High-level events)
        system_events = SystemLog.objects.all().order_by('-timestamp')[:100]
        for event in system_events:
            all_logs.append({
                'timestamp': event.timestamp,
                'user': event.user.username if event.user else 'System',
                'action': event.get_action_display(),
                'action_color': 'primary' if event.action in ['LOGIN', 'LICENSE_ACTIVATE'] else 'secondary',
                'module': 'System',
                'details': f"{event.get_action_display()}: {event.details.get('message', '')}" if event.details else event.get_action_display(),
                'is_system': True
            })

        # Sort combined logs by timestamp descending
        all_logs.sort(key=lambda x: x['timestamp'], reverse=True)
        return all_logs
