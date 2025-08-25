from typing import Any, Type

from django.contrib.auth.mixins import PermissionRequiredMixin
from django.db.models import QuerySet
from django.urls import reverse_lazy
from django.views.generic import (
    CreateView,
    DeleteView,
    DetailView,
    ListView,
    TemplateView,
    UpdateView,
)

from contracts.forms import ContractForm
from contracts.models import Contract


class ContractsListView(PermissionRequiredMixin, ListView):
    """
    """

    permission_required = "contracts.view_contract"
    template_name: str = "contracts/contracts-list.html"
    model: Type[Contract] = Contract
    paginate_by: int = 20
    context_object_name: str = "contracts"


class ContractsDetailView(PermissionRequiredMixin, DetailView):
    """
    """

    permission_required = "contracts.view_contract"
    model: Type[Contract] = Contract
    template_name: str = "contracts/contracts-detail.html"


class ContractsUpdateView(PermissionRequiredMixin, UpdateView):
    """
    """

    permission_required = "contracts.change_contract"
    model: Type[Contract] = Contract
    template_name: str = "contracts/contracts-update.html"
    form_class: Type[ContractForm] = ContractForm


    def get_success_url(self) -> Any:
        """Returns URL to redirect to after successful update."""
        return self.object.get_absolute_url()


class ContractsCreateView(PermissionRequiredMixin, CreateView):
    """
    """

    permission_required = "contracts.add_contract"
    model: Type[Contract] = Contract
    template_name: str = "contracts/contracts-create.html"
    form_class: Type[ContractForm] = ContractForm
    success_url: str = reverse_lazy("contracts:list")


class  ContractDeleteView(PermissionRequiredMixin, DeleteView):
    """
    """

    permission_required = "contracts.delete_contract"
    model: Type[Contract] = Contract
    template_name: str = "contracts/contracts-delete.html"
    success_url: str = reverse_lazy("contracts:list")
