from django.urls import path
from . import views

app_name = "audit"

urlpatterns = [
    path("", views.AuditLogsView.as_view(), name="logs"),
    path("database/", views.DatabaseManagementView.as_view(), name="database"),
    path("database/backup/", views.DatabaseBackupView.as_view(), name="db_backup"),
    path("database/export/", views.DatabaseExportView.as_view(), name="db_export"),
    path("database/import/", views.DatabaseImportView.as_view(), name="db_import"),
]
