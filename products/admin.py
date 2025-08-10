from django.contrib import admin
from django.db.models import QuerySet
from django.http import HttpRequest

from .models import Product


@admin.action(description="Activate selected products")
def activate_products(
    _modeladmin: admin.ModelAdmin,
    request: HttpRequest,
    queryset: QuerySet,
) -> None:
    """Action to activate selected products."""
    queryset.update(is_active=True)


@admin.action(description="Deactivate selected products")
def deactivate_products(
    _modeladmin: admin.ModelAdmin,
    request: HttpRequest,
    queryset: QuerySet,
) -> None:
    """Action to deactivate selected products."""
    queryset.update(is_active=False)


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    """
    Admin interface configuration for Product model.

    Features:
    - List display customization
    - Search functionality
    - List filtering
    - Action for bulk activation/deactivation
    """

    list_display = ("name", "cost", "is_active", "created_at", "updated_at")
    list_filter = ("is_active", "created_at")
    search_fields = ("name", "description")
    list_editable = ("cost", "is_active")
    list_per_page = 20
    date_hierarchy = "created_at"
    ordering = ("-created_at",)
    readonly_fields = ("created_at", "updated_at")
    fieldsets = (
        (
            "Product Information",
            {
                "fields": (
                    "name",
                    "description",
                    "cost",
                ),
            },
        ),
        ("Status", {"fields": ("is_active",)}),
        (
            "Timestamps",
            {"fields": ("created_at", "updated_at"), "classes": ("collapse",)},
        ),
    )
    actions = [
        activate_products,
        deactivate_products,
    ]
