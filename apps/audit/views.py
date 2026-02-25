from django.views import View
from django.shortcuts import render, redirect
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib import messages
from django.core.paginator import Paginator
from django.http import HttpResponse
from django.apps import apps
from django.db import connection
from django.conf import settings
from django.db.models import Q
from django.utils import timezone
from django.utils.decorators import method_decorator
import csv, json, datetime, os, shutil, tempfile

from apps.core.mixins import NonBootstrapRequiredMixin
from apps.core.decorators import tier_required
from .utils import log_system_event


ACTION_COLOR = {
    'Create':             'success',
    'Update':             'info',
    'Delete':             'error',
    'User Login':         'primary',
    'User Logout':        'ghost',
    'Data Export':        'secondary',
    'Setup Step Completed': 'accent',
    'System Initialized': 'accent',
    'License Activated':  'primary',
    'Permission Denied':  'warning',
    'Critical System Error': 'error',
    'Database Backup':    'success',
    'Database Restore':   'warning',
    'Database Import':    'info',
    'Database Export':    'secondary',
    'Database Config Changed': 'accent',
    'Database Access Denied':  'error',
}

ACTION_ICON = {
    'Create':             '✦',
    'Update':             '✎',
    'Delete':             '✕',
    'User Login':         '→',
    'User Logout':        '←',
    'Data Export':        '↓',
    'Setup Step Completed': '⚙',
    'System Initialized': '⚡',
    'License Activated':  '★',
    'Permission Denied':  '⚠',
    'Critical System Error': '☠',
    'Database Backup':    '💾',
    'Database Restore':   '⟲',
    'Database Import':    '⤵',
    'Database Export':    '⤴',
    'Database Config Changed': '⚙',
    'Database Access Denied':  '⛔',
}


# ─── Helpers ──────────────────────────────────────────────────────────────────

def _get_db_info():
    """Return a dict of current database connection metadata."""
    db = settings.DATABASES.get('default', {})
    engine = db.get('ENGINE', '')
    if 'sqlite' in engine:
        db_type = 'SQLite'
        db_name = db.get('NAME', 'db.sqlite3')
        try:
            size_bytes = os.path.getsize(db_name)
            size_str = f"{size_bytes / 1024 / 1024:.2f} MB"
        except OSError:
            size_str = 'Unknown'
        host = 'local file'
        port = '—'
    elif 'postgresql' in engine or 'psycopg' in engine:
        db_type = 'PostgreSQL'
        db_name = db.get('NAME', '')
        size_str = '(query DB for size)'
        host = db.get('HOST', 'localhost')
        port = db.get('PORT', '5432')
    elif 'mysql' in engine:
        db_type = 'MySQL'
        db_name = db.get('NAME', '')
        size_str = '(query DB for size)'
        host = db.get('HOST', 'localhost')
        port = db.get('PORT', '3306')
    else:
        db_type = engine.split('.')[-1]
        db_name = db.get('NAME', '')
        size_str = '—'
        host = db.get('HOST', '—')
        port = db.get('PORT', '—')

    # Table count
    try:
        table_count = len(connection.introspection.table_names())
    except Exception:
        table_count = '?'

    return {
        'type':        db_type,
        'engine':      engine,
        'name':        str(db_name),
        'host':        host,
        'port':        str(port),
        'size':        size_str,
        'table_count': table_count,
    }


# ─── Main Audit Logs View ─────────────────────────────────────────────────────

@method_decorator(tier_required(['pro', 'ultra']), name='dispatch')
class AuditLogsView(LoginRequiredMixin, NonBootstrapRequiredMixin, View):
    template_name = 'pages/audit/logs.html'
    PER_PAGE = 50

    MODELS_TO_TRACK = [
        ('residents',    'Resident',       'Residents'),
        ('certificates', 'Certificate',    'Certificates'),
        ('blotter',      'BlotterCase',    'Blotter'),
        ('business',     'BusinessPermit', 'Business'),
        ('finance',      'OfficialReceipt','Finance'),
    ]

    def _build_logs(self, search='', module_filter='', action_filter='',
                    user_filter='', date_from=None, date_to=None):
        from .models import SystemLog

        all_logs = []

        # 1. Model history (django-simple-history)
        for app_label, model_name, module_name in self.MODELS_TO_TRACK:
            if module_filter and module_filter not in ('All', module_name):
                continue
            system_only_actions = {
                'User Login', 'User Logout', 'Data Export', 'Permission Denied',
                'License Activated', 'System Initialized', 'Setup Step Completed',
                'Critical System Error', 'Database Backup', 'Database Restore',
                'Database Import', 'Database Export', 'Database Config Changed',
                'Database Access Denied',
            }
            if action_filter and action_filter in system_only_actions:
                continue
            try:
                model = apps.get_model(app_label, model_name)
                if not hasattr(model, 'history'):
                    continue
                qs = model.history.all().select_related('history_user')
                if date_from:
                    qs = qs.filter(history_date__gte=date_from)
                if date_to:
                    qs = qs.filter(history_date__lte=date_to)
                if user_filter:
                    qs = qs.filter(history_user__username__icontains=user_filter)
                records = qs.order_by('-history_date')[:200]
                for record in records:
                    action_map = {'+': 'Create', '~': 'Update', '-': 'Delete'}
                    action = action_map.get(record.history_type, 'Unknown')
                    if action_filter and action_filter not in ('All', action):
                        continue
                    user_display = record.history_user.username if record.history_user else 'System'
                    details_str = str(record)
                    if record.history_change_reason:
                        details_str += f' — {record.history_change_reason}'
                    if search and search.lower() not in (user_display + details_str + module_name).lower():
                        continue
                    all_logs.append({
                        'timestamp':    record.history_date,
                        'user':         user_display,
                        'action':       action,
                        'action_color': ACTION_COLOR.get(action, 'ghost'),
                        'action_icon':  ACTION_ICON.get(action, '·'),
                        'module':       module_name,
                        'details':      details_str,
                        'ip':           None,
                        'is_system':    False,
                    })
            except LookupError:
                continue

        # 2. System events
        if not module_filter or module_filter in ('All', 'System', 'Database'):
            qs = SystemLog.objects.select_related('user').order_by('-timestamp')
            if search:
                qs = qs.filter(
                    Q(user__username__icontains=search) |
                    Q(details__icontains=search)
                )
            if user_filter:
                qs = qs.filter(user__username__icontains=user_filter)
            if date_from:
                qs = qs.filter(timestamp__gte=date_from)
            if date_to:
                qs = qs.filter(timestamp__lte=date_to)
            # Filter by module bracket
            if module_filter == 'Database':
                qs = qs.filter(action__startswith='DB_')
            for event in qs[:200]:
                label = event.get_action_display()
                if action_filter and action_filter not in ('All', label):
                    continue
                msg = event.details.get('message', '') if event.details else ''
                details_str = msg if msg else label
                all_logs.append({
                    'timestamp':    event.timestamp,
                    'user':         event.user.username if event.user else 'System',
                    'action':       label,
                    'action_color': ACTION_COLOR.get(label, 'secondary'),
                    'action_icon':  ACTION_ICON.get(label, '·'),
                    'module':       'Database' if event.action.startswith('DB_') else 'System',
                    'details':      details_str,
                    'ip':           str(event.ip_address) if event.ip_address else None,
                    'is_system':    True,
                })

        all_logs.sort(key=lambda x: x['timestamp'], reverse=True)
        return all_logs

    def _parse_date(self, value, end_of_day=False):
        try:
            dt = datetime.datetime.strptime(value.strip(), '%Y-%m-%d')
            if end_of_day:
                dt = dt.replace(hour=23, minute=59, second=59)
            return timezone.make_aware(dt)
        except (ValueError, AttributeError):
            return None

    def _export_response(self, logs, fmt='csv'):
        ts = datetime.datetime.now().strftime('%Y%m%d_%H%M%S')
        if fmt == 'json':
            data = [
                {
                    'timestamp': log['timestamp'].isoformat(),
                    'user': log['user'],
                    'module': log['module'],
                    'action': log['action'],
                    'details': log['details'],
                    'ip': log['ip'] or '',
                }
                for log in logs
            ]
            resp = HttpResponse(json.dumps(data, indent=2), content_type='application/json')
            resp['Content-Disposition'] = f'attachment; filename="audit_logs_{ts}.json"'
        else:
            resp = HttpResponse(content_type='text/csv')
            resp['Content-Disposition'] = f'attachment; filename="audit_logs_{ts}.csv"'
            writer = csv.writer(resp)
            writer.writerow(['Timestamp', 'User', 'Module', 'Action', 'Details', 'IP Address'])
            for log in logs:
                writer.writerow([
                    log['timestamp'].strftime('%Y-%m-%d %H:%M:%S'),
                    log['user'],
                    log['module'],
                    log['action'],
                    log['details'],
                    log['ip'] or '',
                ])
        return resp

    def get(self, request):
        search        = request.GET.get('q', '').strip()
        module_filter = request.GET.get('module', '')
        action_filter = request.GET.get('action', '')
        user_filter   = request.GET.get('user', '').strip()
        date_from     = self._parse_date(request.GET.get('date_from', ''))
        date_to       = self._parse_date(request.GET.get('date_to', ''), end_of_day=True)
        export_fmt    = request.GET.get('format', 'csv')

        all_logs = self._build_logs(
            search=search,
            module_filter=module_filter,
            action_filter=action_filter,
            user_filter=user_filter,
            date_from=date_from,
            date_to=date_to,
        )

        if request.GET.get('export') == 'true':
            return self._export_response(all_logs, fmt=export_fmt)

        page_num  = request.GET.get('page', 1)
        paginator = Paginator(all_logs, self.PER_PAGE)
        page_obj  = paginator.get_page(page_num)

        modules = ['All', 'System', 'Database'] + [m[2] for m in self.MODELS_TO_TRACK]
        actions = ['All', 'Create', 'Update', 'Delete',
                   'User Login', 'User Logout', 'Data Export',
                   'Permission Denied', 'License Activated',
                   'System Initialized', 'Critical System Error',
                   'Database Backup', 'Database Restore', 'Database Import',
                   'Database Export', 'Database Config Changed', 'Database Access Denied']

        return render(request, self.template_name, {
            'page_obj':       page_obj,
            'logs':           page_obj.object_list,
            'total':          paginator.count,
            'search':         search,
            'module_filter':  module_filter,
            'action_filter':  action_filter,
            'user_filter':    user_filter,
            'date_from':      request.GET.get('date_from', ''),
            'date_to':        request.GET.get('date_to', ''),
            'modules':        modules,
            'actions':        actions,
        })


# ─── Database Management View ─────────────────────────────────────────────────

@method_decorator(tier_required(['pro', 'ultra']), name='dispatch')
class DatabaseManagementView(LoginRequiredMixin, NonBootstrapRequiredMixin, View):
    template_name = 'pages/audit/database.html'

    def get(self, request):
        from .models import SystemLog
        db_info = _get_db_info()
        db_logs = SystemLog.objects.filter(
            action__in=['DB_BACKUP', 'DB_RESTORE', 'DB_IMPORT',
                        'DB_EXPORT', 'DB_CONFIG_CHANGE', 'DB_ACCESS_DENIED']
        ).select_related('user').order_by('-timestamp')[:100]

        log_rows = []
        for ev in db_logs:
            label = ev.get_action_display()
            log_rows.append({
                'timestamp':    ev.timestamp,
                'user':         ev.user.username if ev.user else 'System',
                'action':       label,
                'action_color': ACTION_COLOR.get(label, 'ghost'),
                'action_icon':  ACTION_ICON.get(label, '·'),
                'details':      ev.details.get('message', label) if ev.details else label,
                'ip':           str(ev.ip_address) if ev.ip_address else None,
            })

        return render(request, self.template_name, {
            'db_info':      db_info,
            'db_logs':      log_rows,
            'export_apps':  ['residents', 'certificates', 'blotter', 'business',
                             'finance', 'gis', 'core', 'audit'],
        })


# ─── Database Backup View ─────────────────────────────────────────────────────

@method_decorator(tier_required(['pro', 'ultra']), name='dispatch')
class DatabaseBackupView(LoginRequiredMixin, NonBootstrapRequiredMixin, View):

    def post(self, request):
        db = settings.DATABASES.get('default', {})
        engine = db.get('ENGINE', '')

        if 'sqlite' in engine:
            db_path = db.get('NAME', '')
            try:
                ts = datetime.datetime.now().strftime('%Y%m%d_%H%M%S')
                filename = f'backup_{ts}.sqlite3'

                # Stream the SQLite file as a download
                with open(db_path, 'rb') as f:
                    content = f.read()

                log_system_event(
                    'DB_BACKUP', user=request.user, request=request,
                    details={'message': f'SQLite backup downloaded: {filename}',
                             'engine': 'sqlite3', 'filename': filename}
                )

                resp = HttpResponse(content, content_type='application/octet-stream')
                resp['Content-Disposition'] = f'attachment; filename="{filename}"'
                return resp
            except Exception as e:
                log_system_event(
                    'CRITICAL_ERROR', user=request.user, request=request,
                    details={'message': f'Backup failed: {str(e)}'}
                )
                messages.error(request, f"Backup failed: {e}")
        else:
            # For PostgreSQL/MySQL, guide user to use dumpdata or pg_dump
            log_system_event(
                'DB_BACKUP', user=request.user, request=request,
                details={'message': f'Backup initiated for {engine} (dumpdata)',
                         'engine': engine}
            )
            # Run dumpdata and return as JSON
            from django.core.management import call_command
            import io
            buf = io.StringIO()
            try:
                call_command('dumpdata', '--natural-foreign', '--natural-primary',
                             '--indent=2', stdout=buf)
                ts = datetime.datetime.now().strftime('%Y%m%d_%H%M%S')
                resp = HttpResponse(buf.getvalue(), content_type='application/json')
                resp['Content-Disposition'] = f'attachment; filename="backup_{ts}.json"'
                return resp
            except Exception as e:
                messages.error(request, f"Backup failed: {e}")

        return redirect('audit:database')

    def get(self, request):
        return redirect('audit:database')


# ─── Database Export (dumpdata JSON) ─────────────────────────────────────────

@method_decorator(tier_required(['pro', 'ultra']), name='dispatch')
class DatabaseExportView(LoginRequiredMixin, NonBootstrapRequiredMixin, View):

    def post(self, request):
        from django.core.management import call_command
        import io

        selected_apps = request.POST.getlist('apps[]') or None
        fmt = request.POST.get('format', 'json')
        if fmt not in ('json', 'yaml', 'xml'):
            fmt = 'json'

        buf = io.StringIO()
        try:
            args = selected_apps if selected_apps else []
            kwargs = {'stdout': buf, 'format': fmt}
            if fmt == 'json':
                kwargs['indent'] = 2
            call_command('dumpdata', *args, **kwargs)

            ts = datetime.datetime.now().strftime('%Y%m%d_%H%M%S')
            ct_map = {'json': 'application/json', 'yaml': 'text/yaml', 'xml': 'application/xml'}
            ct = ct_map.get(fmt, 'text/plain')
            ext = 'yaml' if fmt == 'yaml' else fmt

            log_system_event(
                'DB_EXPORT', user=request.user, request=request,
                details={'message': f'Dumpdata export ({fmt})',
                         'apps': selected_apps or 'all', 'format': fmt}
            )

            resp = HttpResponse(buf.getvalue(), content_type=ct)
            resp['Content-Disposition'] = f'attachment; filename="export_{ts}.{ext}"'
            return resp
        except Exception as e:
            log_system_event(
                'CRITICAL_ERROR', user=request.user, request=request,
                details={'message': f'DB export failed: {str(e)}'}
            )
            messages.error(request, f"Export failed: {e}")
            return redirect('audit:database')

    def get(self, request):
        return redirect('audit:database')


# ─── Database Import (loaddata) ───────────────────────────────────────────────

@method_decorator(tier_required(['pro', 'ultra']), name='dispatch')
class DatabaseImportView(LoginRequiredMixin, NonBootstrapRequiredMixin, View):

    def post(self, request):
        from django.core.management import call_command

        fixture = request.FILES.get('fixture')
        if not fixture:
            messages.error(request, "No file uploaded.")
            return redirect('audit:database')

        _, ext = os.path.splitext(fixture.name.lower())
        allowed_exts = {'.json', '.yaml', '.yml', '.xml', '.sqlite3'}
        if ext not in allowed_exts:
            messages.error(request, f"Unsupported file type '{ext}'. Accepted: .json, .yaml, .xml, .sqlite3")
            return redirect('audit:database')

        db = settings.DATABASES.get('default', {})
        engine = db.get('ENGINE', '')
        is_sqlite = 'sqlite' in engine

        tmp_path = None
        try:
            with tempfile.NamedTemporaryFile(delete=False, suffix=ext) as tmp:
                for chunk in fixture.chunks():
                    tmp.write(chunk)
                tmp_path = tmp.name

            if ext == '.sqlite3':
                # Raw SQLite file restore — only valid when target DB is also SQLite
                if not is_sqlite:
                    messages.error(
                        request,
                        "Cannot import a .sqlite3 file into a non-SQLite database. "
                        "Export a JSON/YAML fixture from your SQLite database first, "
                        "then import that fixture here."
                    )
                    return redirect('audit:database')

                db_path = str(db.get('NAME', ''))
                shutil.copyfile(tmp_path, db_path)
                log_system_event(
                    'DB_IMPORT', user=request.user, request=request,
                    details={
                        'message': f'SQLite3 database replaced from: {fixture.name}',
                        'filename': fixture.name,
                        'size_bytes': fixture.size,
                        'format': 'sqlite3',
                    }
                )
                messages.success(request, f"✓ '{fixture.name}' restored as the active SQLite database.")

            else:
                # Django fixture formats — cross-compatible with any DB engine
                # Map yaml alias
                fmt = 'yaml' if ext in ('.yaml', '.yml') else ext.lstrip('.')
                call_command('loaddata', tmp_path, verbosity=0)
                log_system_event(
                    'DB_IMPORT', user=request.user, request=request,
                    details={
                        'message': f'Fixture imported: {fixture.name}',
                        'filename': fixture.name,
                        'size_bytes': fixture.size,
                        'format': fmt,
                    }
                )
                messages.success(request, f"✓ '{fixture.name}' ({fmt.upper()}) imported successfully.")

        except Exception as e:
            log_system_event(
                'CRITICAL_ERROR', user=request.user, request=request,
                details={'message': f'Import failed: {str(e)}', 'filename': fixture.name}
            )
            messages.error(request, f"Import failed: {e}")
        finally:
            if tmp_path:
                try:
                    os.unlink(tmp_path)
                except Exception:
                    pass

        return redirect('audit:database')

    def get(self, request):
        return redirect('audit:database')
