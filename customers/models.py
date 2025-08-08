from typing import Any

from django.db import models
from django.urls import reverse
from django.utils.translation import gettext_lazy as _

from crm.models import BaseModel


class Customer(BaseModel):
    """Represents an active customer in the CRM system.

    Attributes:
        lead (Lead): Original lead that became a customer (OneToOne to Lead).
        contract (Contract): Active contract for this customer (FK to Contract).

    Methods:
        get_absolute_url(): Returns URL for customer detail view.
    """

    class Meta:
        """Metadata options for the Customers model."""

        verbose_name = _("Customer")
        verbose_name_plural = _("Customers")
        ordering = ["-created_at"]

    lead = models.OneToOneField(
        "leads.Lead",
        on_delete=models.PROTECT,
        related_name="customer",
        verbose_name=_("Lead"),
        help_text=_("Original lead that became a customer"),
    )

    contract = models.ForeignKey(
        "contracts.Contract",
        on_delete=models.PROTECT,
        related_name="customers",
        verbose_name=_("Contract"),
        help_text=_("Active contract for this customer"),
    )

    def __str__(self) -> str:
        """String representation of the customer."""

        return f"Customer(pk={self.pk})"

    def get_absolute_url(self) -> Any:
        """Returns the absolute URL to view this customer.

        Returns:
            str: Absolute URL for customer detail view.
        """

        return reverse("customer:detail", kwargs={"pk": self.pk})
