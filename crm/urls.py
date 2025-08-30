from django.urls import path

from crm.views import dashboard_view

app_name = "crm"

urlpatterns: list[path] = [
    path("", dashboard_view, name="dashboard"),
]
