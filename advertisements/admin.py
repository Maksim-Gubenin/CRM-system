from django.contrib import admin

from .models import Advertisement


@admin.register(Advertisement)
class AdvertisementAdmin(admin.ModelAdmin):
    """
    Admin interface configuration for Advertisement model.

    Features:
    - List display customization with advertisement details and metrics
    - Filtering by channel, activity status, and creation date
    - Search functionality by advertisement name
    - Pagination configuration
    """

    list_display = ("name", "channel", "cost", "leads_count", "is_active", "created_at")
    list_filter = (
        "channel",
        "is_active",
        "created_at",
    )
    search_fields = ("name",)
    list_per_page = 20
