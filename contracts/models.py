from typing import Any

from django.core.exceptions import ValidationError
from django.core.validators import FileExtensionValidator, MinValueValidator
from django.db import models
from django.urls import reverse
from django.utils.translation import gettext_lazy as _

from crm.models import BaseModel


class Contract(BaseModel):
    """Represents a signed contract with a customer in the CRM system.

    Attributes:
        name (str): Contract name/identifier. Max length 255 chars.
        product (Product): Service/product covered by contract (FK to Product).
        document (File): Scanned contract document (PDF or Word).
        start_date (date): Service start date.
        end_date (date): Service end date.
        cost (Decimal): Total contract value (12 digits, 2 decimal places).

    Methods:
        clean(): Validates that end_date is not earlier than start_date.
        get_absolute_url(): Returns URL for contract detail view.
    """

    class Meta:
        """Metadata options for the Contracts model."""

        verbose_name = _("Contract")
        verbose_name_plural = _("Contracts")
        ordering = ["-cost"]

    name = models.CharField(
        max_length=255,
        verbose_name=_("Contract name"),
        help_text=_("Official contract reference number/name"),
    )

    product = models.ForeignKey(
        "products.Product",
        on_delete=models.PROTECT,
        verbose_name=_("Product"),
        help_text=_("Service/product covered by this contract"),
    )


    document = models.FileField(
        upload_to="contracts/%Y/%m/",
        validators=[
            FileExtensionValidator(
                ["pdf", "doc", "docx"],
            ),
        ],
        verbose_name=_("Document"),
        help_text=_("Scanned contract file (PDF or Word)"),
    )

    start_date = models.DateField(
        verbose_name=_("Start date"),
        help_text=_("Service start date"),
    )

    end_date = models.DateField(
        verbose_name=_("End date"),
        help_text=_("Service end date"),
    )

    cost = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        validators=[
            MinValueValidator(0),
        ],
        verbose_name=_("Cost"),
        help_text=_("Total contract value"),
    )

    def __str__(self) -> str:
        """String representation: '[Name] - Customer (Product)'"""

        return f"Contract(pk={self.pk}, name={self.name})"

    def clean(self) -> None:
        """Validates contract dates."""

        if self.end_date < self.start_date:
            raise ValidationError(_("End date cannot be earlier than start date"))
        super().clean()

    def get_absolute_url(self) -> Any:
        """Returns the absolute URL to view this contract.

        Returns:
            str: Absolute URL for contract detail view.
        """

        return reverse("contracts:detail", kwargs={"pk": self.pk})
