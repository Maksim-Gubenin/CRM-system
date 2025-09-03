from typing import Any, Dict, Type

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

from advertisements.forms import ADSForm
from advertisements.models import Advertisement as ads
from crm.mixins import (
    CreateLoggingMixin,
    DeleteLoggingMixin,
    DetailLoggingMixin,
    ListLoggingMixin,
    PerformanceLoggingMixin,
    UpdateLoggingMixin,
)


class ADSListView(
    ListLoggingMixin, PerformanceLoggingMixin, PermissionRequiredMixin, ListView
):
    """
    Displays a paginated list of active advertisements.

    Attributes:
        permission_required (str): Permission required to access this view
        template_name (str): Path to the template used for rendering
        model (Type[ads]): Model class this view operates on
        paginate_by (int): Number of items per page
        context_object_name (str): Name of the context variable containing
            the advertisement list
        queryset (QuerySet[ads]): Base queryset filtered to show
            only active advertisements
    """

    permission_required = "advertisements.view_advertisement"
    template_name: str = "advertisements/ads-list.html"
    model: Type[ads] = ads
    paginate_by: int = 20
    context_object_name: str = "ads"
    queryset = ads.objects.filter(is_active=True).all()


class ADSDetailView(
    DetailLoggingMixin, PerformanceLoggingMixin, PermissionRequiredMixin, DetailView
):
    """
    Displays detailed information about a single active advertisement.

    Attributes:
        permission_required (str): Permission required to access this view
        model (Type[ads]): Model class this view operates on
        template_name (str): Path to the template used for rendering
    """

    permission_required = "advertisements.view_advertisement"
    model: Type[ads] = ads
    template_name: str = "advertisements/ads-detail.html"

    def get_queryset(self) -> QuerySet[ads]:
        """Returns queryset filtered to only include active advertisements."""
        return super().get_queryset().filter(is_active=True)


class ADSUpdateView(
    UpdateLoggingMixin, PerformanceLoggingMixin, PermissionRequiredMixin, UpdateView
):
    """
    Handles editing of an existing active advertisement.

    Attributes:
        permission_required (str): Permission required to access this view
        model (Type[ads]): Model class this view operates on
        template_name (str): Path to the template used for rendering
        form_class (Type[ADSForm]): Form class used for editing
    """

    permission_required = "advertisements.change_advertisement"
    model: Type[ads] = ads
    template_name: str = "advertisements/ads-update.html"
    form_class: Type[ADSForm] = ADSForm

    def get_queryset(self) -> QuerySet[ads]:
        """Returns queryset filtered to only include active advertisements."""
        return super().get_queryset().filter(is_active=True)

    def get_success_url(self) -> Any:
        """Returns URL to redirect to after successful update."""
        return self.object.get_absolute_url()


class ADSCreateView(
    CreateLoggingMixin, PerformanceLoggingMixin, PermissionRequiredMixin, CreateView
):
    """
    Handles creation of new advertisements.

    Attributes:
        permission_required (str): Permission required to access this view
        model (Type[ads]): Model class this view operates on
        template_name (str): Path to the template used for rendering
        form_class (Type[ADSForm]): Form class used for creation
        success_url (str): URL to redirect to after successful creation
    """

    permission_required = "advertisements.add_advertisement"
    model: Type[ads] = ads
    template_name: str = "advertisements/ads-create.html"
    form_class: Type[ADSForm] = ADSForm
    success_url: str = reverse_lazy("advertisements:list")


class ADSDeleteView(
    DeleteLoggingMixin, PerformanceLoggingMixin, PermissionRequiredMixin, DeleteView
):
    """
    Handles deletion of active advertisements.

    Attributes:
        permission_required (str): Permission required to access this view
        model (Type[ads]): Model class this view operates on
        template_name (str): Path to the template used for rendering
        success_url (str): URL to redirect to after successful deletion
    """

    permission_required = "advertisements.delete_advertisement"
    model: Type[ads] = ads
    template_name: str = "advertisements/ads-delete.html"
    success_url: str = reverse_lazy("advertisements:list")

    def get_queryset(self) -> QuerySet[ads]:
        """Returns queryset filtered to only include active advertisements."""
        return super().get_queryset().filter(is_active=True)


class ADSStatisticsView(PerformanceLoggingMixin, PermissionRequiredMixin, TemplateView):
    """
    View for displaying advertising campaign statistics.

    Attributes:
        permission_required (str): Permission required to access this view
        template_name (str): Path to the template used for rendering
    """

    permission_required = "advertisements.view_advertisement_stats"
    template_name = "advertisements/ads-statistic.html"

    def get_context_data(self, **kwargs: Any) -> Dict[str, Any]:
        """
        Returns context data with advertisement statistics.

        Returns:
            Dict[str, Any]: Context containing all advertisements for statistics display
        """
        context: dict[str, Any] = super().get_context_data(**kwargs)
        advertisements = ads.objects.all()
        context["ads"] = advertisements
        return context
