from django.urls import path

from leads.views import LeadsDetailView, LeadsListView, LeadsUpdateView

app_name = "leads"

urlpatterns: list[path] = [
    path("", LeadsListView.as_view(), name="list"),
    path("<int:pk>/",LeadsDetailView.as_view(), name="detail"),
    # path("create/", ProductsCreateView.as_view(), name="create"),
    path("<int:pk>/update/", LeadsUpdateView.as_view(), name="update"),
    # path("<int:pk>/delete/", ProductsDeleteView.as_view(), name="delete"),
]
