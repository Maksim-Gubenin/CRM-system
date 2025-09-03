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

from crm.mixins import (
    CreateLoggingMixin,
    DeleteLoggingMixin,
    DetailLoggingMixin,
    ListLoggingMixin,
    PerformanceLoggingMixin,
    UpdateLoggingMixin,
)
from products.forms import ProductForm
from products.models import Product


class ProductsListView(
    ListLoggingMixin, PerformanceLoggingMixin, PermissionRequiredMixin, ListView
):
    """
    Displays a paginated list of active products.

    Attributes:
        template_name (str): Path to the template used for rendering
        model (Type[Product]): Model class this view operates on
        paginate_by (int): Number of items per page
        context_object_name (str): Name of the context variable containing
            the product list
        queryset (QuerySet[Product]): Base queryset filtered to show
            only active products
    """

    permission_required = "products.view_product"
    template_name: str = "products/products-list.html"
    model: Type[Product] = Product
    paginate_by: int = 20
    context_object_name: str = "products"
    queryset = Product.objects.filter(is_active=True)


class ProductsDetailView(
    DetailLoggingMixin, PerformanceLoggingMixin, PermissionRequiredMixin, DetailView
):
    """
    Displays detailed information about a single active product.

    Attributes:
        model (Type[Product]): Model class this view operates on
        template_name (str): Path to the template used for rendering
    """

    permission_required = "products.view_product"
    model: Type[Product] = Product
    template_name: str = "products/products-detail.html"

    def get_queryset(self) -> QuerySet[Product]:
        return super().get_queryset().filter(is_active=True)


class ProductsUpdateView(
    UpdateLoggingMixin, PerformanceLoggingMixin, PermissionRequiredMixin, UpdateView
):
    """
    Handles editing of an existing active product.

    Attributes:
        model (Type[Product]): Model class this view operates on
        template_name (str): Path to the template used for rendering
        form_class (Type[ProductForm]): Form class used for editing
    """

    permission_required = "products.change_product"
    model: Type[Product] = Product
    template_name: str = "products/products-update.html"
    form_class: Type[ProductForm] = ProductForm

    def get_queryset(self) -> QuerySet[Product]:
        """Returns queryset filtered to only include active products."""
        return super().get_queryset().filter(is_active=True)

    def get_success_url(self) -> Any:
        """Returns URL to redirect to after successful update."""
        return self.object.get_absolute_url()


class ProductsCreateView(
    CreateLoggingMixin, PerformanceLoggingMixin, PermissionRequiredMixin, CreateView
):
    """
    Handles creation of new products.

    Attributes:
        model (Type[Product]): Model class this view operates on
        template_name (str): Path to the template used for rendering
        form_class (Type[ProductForm]): Form class used for creation
        success_url (str): URL to redirect to after successful creation
    """

    permission_required = "products.add_product"
    model: Type[Product] = Product
    template_name: str = "products/products-create.html"
    form_class: Type[ProductForm] = ProductForm
    success_url: str = reverse_lazy("products:list")


class ProductsDeleteView(
    DeleteLoggingMixin, PerformanceLoggingMixin, PermissionRequiredMixin, DeleteView
):
    """
    Handles deletion of active products.

    Attributes:
        model (Type[Product]): Model class this view operates on
        template_name (str): Path to the template used for rendering
        success_url (str): URL to redirect to after successful deletion
    """

    permission_required = "products.delete_product"
    model: Type[Product] = Product
    template_name: str = "products/products-delete.html"
    success_url: str = reverse_lazy("products:list")

    def get_queryset(self) -> QuerySet[Product]:
        """Returns queryset filtered to only include active products."""
        return super().get_queryset().filter(is_active=True)
