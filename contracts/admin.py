from django.contrib import admin
from django.http import HttpRequest

from .models import Contract


@admin.register(Contract)
class ContractAdmin(admin.ModelAdmin):
    """
    Admin interface configuration for Contract model.

    Provides management interface for contracts with list display,
    filtering, search functionality, and organized field grouping.
    """

    list_display = (
        "name",
        "product",
        "start_date",
        "end_date",
        "cost",
        "created_at"
    )

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
        ("Contract Information", {
            "fields": (
                "name",
                "product",
            )
        }),
        ("Dates & Financial", {
            "fields": (
                "start_date",
                "end_date",
                "cost",
            )
        }),
        ("Document", {
            "fields": (
                "document",
            )
        }),
    )

    def get_readonly_fields(self, request: HttpRequest, obj: Contract = None) -> tuple:
        """
        Return readonly fields based on object state.
        """
        if obj:
            return ("created_at", "updated_at")
        return ()
