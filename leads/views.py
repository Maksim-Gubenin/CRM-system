from typing import Any, Type

from django.contrib.auth.mixins import PermissionRequiredMixin
from django.db.models import QuerySet
from django.urls import reverse_lazy
from django.views.generic import (
    CreateView,
    DeleteView,
    DetailView,
    ListView,
    UpdateView,
)

from leads.forms import LeadForm
from leads.models import Lead


class LeadsListView(PermissionRequiredMixin, ListView):
    """
    """

    permission_required = "leads.view_lead"
    template_name: str = "leads/leads-list.html"
    model: Type[Lead] = Lead
    paginate_by: int = 20
    context_object_name: str = "leads"


class LeadsDetailView(PermissionRequiredMixin, DetailView):
    """
    """

    permission_required = "leads.view_lead"
    model: Type[Lead] = Lead
    template_name: str = "leads/leads-detail.html"


class LeadsUpdateView(PermissionRequiredMixin, UpdateView):
    """
    Handles editing of an existing active product.

    Attributes:
        model (Type[Product]): Model class this view operates on
        template_name (str): Path to the template used for rendering
        form_class (Type[ProductForm]): Form class used for editing
    """

    permission_required = "leads.change_lead"
    model: Type[Lead] = Lead
    template_name: str = "leads/leads-update.html"
    form_class: Type[LeadForm] = LeadForm

    def get_success_url(self) -> Any:
        """Returns URL to redirect to after successful update."""
        return self.object.get_absolute_url()


# class ProductsCreateView(PermissionRequiredMixin, CreateView):
#     """
#     Handles creation of new products.

#     Attributes:
#         model (Type[Product]): Model class this view operates on
#         template_name (str): Path to the template used for rendering
#         form_class (Type[ProductForm]): Form class used for creation
#         success_url (str): URL to redirect to after successful creation
#     """

#     permission_required = "products.add_product"
#     model: Type[Product] = Product
#     template_name: str = "products/products-create.html"
#     form_class: Type[ProductForm] = ProductForm
#     success_url: str = reverse_lazy("products:list")


# class ProductsDeleteView(PermissionRequiredMixin, DeleteView):
#     """
#     Handles deletion of active products.

#     Attributes:
#         model (Type[Product]): Model class this view operates on
#         template_name (str): Path to the template used for rendering
#         success_url (str): URL to redirect to after successful deletion
#     """

#     permission_required = "products.delete_product"
#     model: Type[Product] = Product
#     template_name: str = "products/products-delete.html"
#     success_url: str = reverse_lazy("products:list")

#     def get_queryset(self) -> QuerySet[Product]:
#         """Returns queryset filtered to only include active products."""
#         return super().get_queryset().filter(is_active=True)
