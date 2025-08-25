from django.urls import path

from contracts.views import ContractsListView, ContractsDetailView, ContractsUpdateView, ContractsCreateView, ContractDeleteView

app_name = "contracts"

urlpatterns: list[path] = [
    path("", ContractsListView.as_view(), name="list"),
    path("<int:pk>/", ContractsDetailView.as_view(), name="detail"),
    path("create/", ContractsCreateView.as_view(), name="create"),
    path("<int:pk>/update/", ContractsUpdateView.as_view(), name="update"),
    path("<int:pk>/delete/", ContractDeleteView.as_view(), name="delete"),
]
