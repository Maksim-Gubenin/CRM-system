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

from crm.mixins import (
    CreateLoggingMixin,
    DeleteLoggingMixin,
    DetailLoggingMixin,
    ListLoggingMixin,
    PerformanceLoggingMixin,
    UpdateLoggingMixin,
)
from customers.forms import CustomerForm
from customers.models import Customer


class CustomersListView(
    ListLoggingMixin, PerformanceLoggingMixin, PermissionRequiredMixin, ListView
):
    """
    Displays a paginated list of all active customers.

    Attributes:
        permission_required (str): Permission required to access this view
        template_name (str): Path to the template used for rendering
        model (Type[Customer]): Model class this view operates on
        paginate_by (int): Number of items per page
        context_object_name (str): Name of the context variable containing
            the customers list
    """

    permission_required = "customers.view_customer"
    template_name: str = "customers/customers-list.html"
    model: Type[Customer] = Customer
    paginate_by: int = 20
    context_object_name: str = "customers"


class CustomersDetailView(
    DetailLoggingMixin, PerformanceLoggingMixin, PermissionRequiredMixin, DetailView
):
    """
    Displays detailed information about a single customer.

    Attributes:
        permission_required (str): Permission required to access this view
        model (Type[Customer]): Model class this view operates on
        template_name (str): Path to the template used for rendering
    """

    permission_required = "customers.view_customer"
    model: Type[Customer] = Customer
    template_name: str = "customers/customers-detail.html"


class CustomersUpdateView(
    UpdateLoggingMixin, PerformanceLoggingMixin, PermissionRequiredMixin, UpdateView
):
    """
    Handles editing of an existing customer.

    Attributes:
        permission_required (str): Permission required to access this view
        model (Type[Customer]): Model class this view operates on
        template_name (str): Path to the template used for rendering
        form_class (Type[CustomerForm]): Form class used for editing
    """

    permission_required = "customers.change_customer"
    model: Type[Customer] = Customer
    template_name: str = "customers/customers-update.html"
    form_class: Type[CustomerForm] = CustomerForm

    def get_success_url(self) -> Any:
        """Returns URL to redirect to after successful update."""
        return self.object.get_absolute_url()


class CustomersCreateView(
    CreateLoggingMixin, PerformanceLoggingMixin, PermissionRequiredMixin, CreateView
):
    """
    Handles creation of new customers.

    Attributes:
        permission_required (str): Permission required to access this view
        model (Type[Customer]): Model class this view operates on
        template_name (str): Path to the template used for rendering
        form_class (Type[CustomerForm]): Form class used for creation
        success_url (str): URL to redirect to after successful creation
    """

    permission_required = "customers.add_customer"
    model: Type[Customer] = Customer
    template_name: str = "customers/customers-create.html"
    form_class: Type[CustomerForm] = CustomerForm
    success_url: str = reverse_lazy("customers:list")


class CustomersDeleteView(
    DeleteLoggingMixin, PerformanceLoggingMixin, PermissionRequiredMixin, DeleteView
):
    """
    Handles deletion of customers.

    Attributes:
        permission_required (str): Permission required to access this view
        model (Type[Customer]): Model class this view operates on
        template_name (str): Path to the template used for rendering
        success_url (str): URL to redirect to after successful deletion
    """

    permission_required = "customers.delete_customer"
    model: Type[Customer] = Customer
    template_name: str = "customers/customers-delete.html"
    success_url: str = reverse_lazy("customers:list")
