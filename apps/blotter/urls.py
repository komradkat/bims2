from django.urls import path
from . import views

app_name = "blotter"

urlpatterns = [
    path("", views.BlotterListView.as_view(), name="list"),
    path("add/", views.BlotterCreateView.as_view(), name="add"),
    path("<int:pk>/", views.BlotterDetailView.as_view(), name="detail"),
    path(
        "<int:case_id>/hearings/add/",
        views.HearingCreateView.as_view(),
        name="hearing_add",
    ),
    path(
        "<int:pk>/status/update/",
        views.CaseStatusUpdateView.as_view(),
        name="status_update",
    ),
]
