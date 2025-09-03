from typing import Any, Type

from django.contrib.auth.mixins import PermissionRequiredMixin
from django.urls import reverse_lazy
from django.views.generic import (
    CreateView,
    DeleteView,
    DetailView,
    ListView,
    UpdateView,
)

from contracts.forms import ContractForm
from contracts.models import Contract
from crm.mixins import (
    CreateLoggingMixin,
    DeleteLoggingMixin,
    DetailLoggingMixin,
    ListLoggingMixin,
    PerformanceLoggingMixin,
    UpdateLoggingMixin,
)


class ContractsListView(
    ListLoggingMixin, PerformanceLoggingMixin, PermissionRequiredMixin, ListView
):
    """
    Displays a paginated list of all contracts.

    Attributes:
        permission_required (str): Permission required to access this view
        template_name (str): Path to the template used for rendering
        model (Type[Contract]): Model class this view operates on
        paginate_by (int): Number of items per page
        context_object_name (str): Name of the context variable containing
            the contracts list
    """

    permission_required = "contracts.view_contract"
    template_name: str = "contracts/contracts-list.html"
    model: Type[Contract] = Contract
    paginate_by: int = 20
    context_object_name: str = "contracts"


class ContractsDetailView(
    DetailLoggingMixin, PerformanceLoggingMixin, PermissionRequiredMixin, DetailView
):
    """
    Displays detailed information about a single contract.

    Attributes:
        permission_required (str): Permission required to access this view
        model (Type[Contract]): Model class this view operates on
        template_name (str): Path to the template used for rendering
    """

    permission_required = "contracts.view_contract"
    model: Type[Contract] = Contract
    template_name: str = "contracts/contracts-detail.html"


class ContractsUpdateView(
    UpdateLoggingMixin, PerformanceLoggingMixin, PermissionRequiredMixin, UpdateView
):
    """
    Handles editing of an existing contract.

    Attributes:
        permission_required (str): Permission required to access this view
        model (Type[Contract]): Model class this view operates on
        template_name (str): Path to the template used for rendering
        form_class (Type[ContractForm]): Form class used for editing
    """

    permission_required = "contracts.change_contract"
    model: Type[Contract] = Contract
    template_name: str = "contracts/contracts-update.html"
    form_class: Type[ContractForm] = ContractForm

    def get_success_url(self) -> Any:
        """Returns URL to redirect to after successful update."""
        return self.object.get_absolute_url()


class ContractsCreateView(
    CreateLoggingMixin, PerformanceLoggingMixin, PermissionRequiredMixin, CreateView
):
    """
    Handles creation of new contracts.

    Attributes:
        permission_required (str): Permission required to access this view
        model (Type[Contract]): Model class this view operates on
        template_name (str): Path to the template used for rendering
        form_class (Type[ContractForm]): Form class used for creation
        success_url (str): URL to redirect to after successful creation
    """

    permission_required = "contracts.add_contract"
    model: Type[Contract] = Contract
    template_name: str = "contracts/contracts-create.html"
    form_class: Type[ContractForm] = ContractForm
    success_url: str = reverse_lazy("contracts:list")


class ContractDeleteView(
    DeleteLoggingMixin, PerformanceLoggingMixin, PermissionRequiredMixin, DeleteView
):
    """
    Handles deletion of contracts.

    Attributes:
        permission_required (str): Permission required to access this view
        model (Type[Contract]): Model class this view operates on
        template_name (str): Path to the template used for rendering
        success_url (str): URL to redirect to after successful deletion
    """

    permission_required = "contracts.delete_contract"
    model: Type[Contract] = Contract
    template_name: str = "contracts/contracts-delete.html"
    success_url: str = reverse_lazy("contracts:list")
