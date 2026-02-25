from django.urls import path
from . import views

app_name = "business"

urlpatterns = [
    path("", views.BusinessListView.as_view(), name="list"),
    path("add/", views.BusinessCreateView.as_view(), name="add"),
    path("<int:pk>/edit/", views.BusinessUpdateView.as_view(), name="edit"),
]
