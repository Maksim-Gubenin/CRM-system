from django.contrib import admin

from .models import Lead


@admin.register(Lead)
class LeadAdmin(admin.ModelAdmin):
    """
    Admin interface configuration for Lead model.

    Provides basic CRUD operations and filtering for lead management
    in Django administration interface.

    Features:
    - List display with key lead information
    - Filtering by creation date and advertisement source
    - Search functionality across main lead attributes
    - Organized field grouping in edit forms
    """

    list_display = (
        "last_name",
        "first_name",
        "phone",
        "email",
        "advertisement",
        "created_at",
    )

    list_filter = (
        "created_at",
        "advertisement",
    )

    search_fields = (
        "first_name",
        "last_name",
        "phone",
        "email",
    )

    list_per_page = 20

    fieldsets = (
        (
            "Personal Information",
            {
                "fields": (
                    "first_name",
                    "last_name",
                    "middle_name",
                )
            },
        ),
        (
            "Contact Information",
            {
                "fields": (
                    "phone",
                    "email",
                )
            },
        ),
        ("Marketing", {"fields": ("advertisement",)}),
    )
