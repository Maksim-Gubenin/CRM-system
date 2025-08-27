from django.urls import path

from customers.views import (
    CustomersCreateView,
    CustomersDeleteView,
    CustomersDetailView,
    CustomersListView,
    CustomersUpdateView,
)

app_name = "customers"

urlpatterns: list[path] = [
    path("", CustomersListView.as_view(), name="list"),
    path("<int:pk>/", CustomersDetailView.as_view(), name="detail"),
    path("create/", CustomersCreateView.as_view(), name="create"),
    path("<int:pk>/update/", CustomersUpdateView.as_view(), name="update"),
    path("<int:pk>/delete/", CustomersDeleteView.as_view(), name="delete"),
]
urlpatterns: list[path] = [
    path("", CustomersListView.as_view(), name="list"),
    path("<int:pk>/", CustomersDetailView.as_view(), name="detail"),
    path("create/", CustomersCreateView.as_view(), name="create"),
    path("<int:pk>/update/", CustomersUpdateView.as_view(), name="update"),
    path("<int:pk>/delete/", CustomersDeleteView.as_view(), name="delete"),
]
