from typing import Optional

from django.contrib import admin
from django.http import HttpRequest

from .models import Contract


@admin.register(Contract)
class ContractAdmin(admin.ModelAdmin):
    """
    Admin interface configuration for Contract model.

    Features:
    - List display with contract details and key information
    - Filtering by dates, product, and creation time
    - Search functionality across contract names and products
    - Organized field grouping in edit forms
    - Automatic readonly fields management for timestamps
    """

    list_display = ("name", "product", "start_date", "end_date", "cost", "created_at")

    list_filter = (
        "start_date",
        "end_date",
        "product",
        "created_at",
    )

    search_fields = (
        "name",
        "product__name",
    )

    list_per_page = 20

    fieldsets = (
        (
            "Contract Information",
            {
                "fields": (
                    "name",
                    "product",
                )
            },
        ),
        (
            "Dates & Financial",
            {
                "fields": (
                    "start_date",
                    "end_date",
                    "cost",
                )
            },
        ),
        ("Document", {"fields": ("document",)}),
    )

    def get_readonly_fields(
        self, request: HttpRequest, obj: Optional[Contract] = None
    ) -> Optional[tuple]:
        """
        Return readonly fields based on object state.

        Args:
            request: The current HTTP request
            obj: The Contract instance being edited (None for new objects)

        Returns:
            tuple: Readonly fields for the form
        """

        if obj:
            return ("created_at", "updated_at")
        return ()
