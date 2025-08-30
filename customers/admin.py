from typing import Optional

from django.contrib import admin
from django.http import HttpRequest

from .models import Customer


@admin.register(Customer)
class CustomerAdmin(admin.ModelAdmin):
    """
    Admin interface configuration for Customer model.

    Provides management interface for active customers with list display,
    filtering, search functionality, and organized field grouping.
    """

    list_display = ("id", "lead_info", "contract_info", "created_at")

    list_filter = ("created_at",)

    search_fields = (
        "lead__first_name",
        "lead__last_name",
        "lead__email",
        "lead__phone",
        "contract__name",
    )

    list_per_page = 20

    fieldsets = (
        (
            "Customer Information",
            {
                "fields": (
                    "lead",
                    "contract",
                )
            },
        ),
    )

    readonly_fields = ("created_at", "updated_at")

    def lead_info(self, obj: Customer) -> str:
        """Display lead information in list view."""
        if obj.lead:
            return f"{obj.lead.last_name} {obj.lead.first_name} ({obj.lead.phone})"
        return "-"

    def contract_info(self, obj: Customer) -> str:
        """Display contract information in list view."""
        if obj.contract:
            return f"{obj.contract.name} - {obj.contract.cost}"
        return "-"

    def get_readonly_fields(
        self, request: HttpRequest, obj: Optional[Customer] = None
    ) -> tuple:
        """
        Return readonly fields based on object state.
        """
        if obj:
            return ("created_at", "updated_at")
        return ()
