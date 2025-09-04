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
from leads.forms import LeadForm
from leads.models import Lead


class LeadsListView(
    ListLoggingMixin, PerformanceLoggingMixin, PermissionRequiredMixin, ListView
):
    """
    Displays a paginated list of all leads.

    Attributes:
        permission_required (str): Permission required to access this view
        template_name (str): Path to the template used for rendering
        model (Type[Lead]): Model class this view operates on
        paginate_by (int): Number of items per page
        context_object_name (str): Name of the context variable containing
            the leads list
    """

    permission_required = "leads.view_lead"
    template_name: str = "leads/leads-list.html"
    model: Type[Lead] = Lead
    paginate_by: int = 20
    context_object_name: str = "leads"


class LeadsDetailView(
    DetailLoggingMixin, PerformanceLoggingMixin, PermissionRequiredMixin, DetailView
):
    """
    Displays detailed information about a single lead.

    Attributes:
        permission_required (str): Permission required to access this view
        model (Type[Lead]): Model class this view operates on
        template_name (str): Path to the template used for rendering
    """

    permission_required = "leads.view_lead"
    model: Type[Lead] = Lead
    template_name: str = "leads/leads-detail.html"


class LeadsUpdateView(
    UpdateLoggingMixin, PerformanceLoggingMixin, PermissionRequiredMixin, UpdateView
):
    """
    Handles editing of an existing lead.

    Attributes:
        permission_required (str): Permission required to access this view
        model (Type[Lead]): Model class this view operates on
        template_name (str): Path to the template used for rendering
        form_class (Type[LeadForm]): Form class used for editing
    """

    permission_required = "leads.change_lead"
    model: Type[Lead] = Lead
    template_name: str = "leads/leads-update.html"
    form_class: Type[LeadForm] = LeadForm

    def get_success_url(self) -> Any:
        """Returns URL to redirect to after successful update."""
        return self.object.get_absolute_url()


class LeadsCreateView(
    CreateLoggingMixin, PerformanceLoggingMixin, PermissionRequiredMixin, CreateView
):
    """
    Handles creation of new leads.

    Attributes:
        permission_required (str): Permission required to access this view
        model (Type[Lead]): Model class this view operates on
        template_name (str): Path to the template used for rendering
        form_class (Type[LeadForm]): Form class used for creation
        success_url (str): URL to redirect to after successful creation
    """

    permission_required = "leads.add_lead"
    model: Type[Lead] = Lead
    template_name: str = "leads/leads-create.html"
    form_class: Type[LeadForm] = LeadForm
    success_url: str = reverse_lazy("leads:list")


class LeadsDeleteView(
    DeleteLoggingMixin, PerformanceLoggingMixin, PermissionRequiredMixin, DeleteView
):
    """
    Handles deletion of leads.

    Attributes:
        permission_required (str): Permission required to access this view
        model (Type[Lead]): Model class this view operates on
        template_name (str): Path to the template used for rendering
        success_url (str): URL to redirect to after successful deletion
    """

    permission_required = "leads.delete_lead"
    model: Type[Lead] = Lead
    template_name: str = "leads/leads-delete.html"
    success_url: str = reverse_lazy("leads:list")
