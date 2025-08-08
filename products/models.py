from typing import Any

from django.core.validators import MinValueValidator
from django.db import models
from django.urls import reverse
from django.utils.translation import gettext_lazy as _

from crm.models import BaseModel


class Product(BaseModel):
    """Represents a service or product offered by the company.

    Attributes:
        name (str): Product name (255 chars max).
        description (str|None): Detailed description (optional).
        cost (Decimal): Price (10 digits, 2 decimals, non-negative).
        is_active (bool): Whether product is currently offered.

    Properties:
        short_description: First 50 chars of description or placeholder.

    Methods:
        get_absolute_url(): Returns URL for product detail view.
    """

    class Meta:
        """Metadata options for the Product model."""

        verbose_name = _("Product")
        verbose_name_plural = _("Products")
        ordering = ["name"]
        indexes = [
            models.Index(fields=["name"], name="product_name_idx"),
            models.Index(fields=["cost"], name="product_cost_idx"),
        ]

    name = models.CharField(
        max_length=255,
        verbose_name=_("Name"),
        help_text=_("Official name of the service/product"),
    )
    description = models.TextField(
        blank=True,
        null=True,
        verbose_name=_("Description"),
        help_text=_("Detailed description of the service"),
    )
    cost = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        validators=[MinValueValidator(0, message=_("Cost cannot be negative"))],
        verbose_name=_("Cost"),
        help_text=_("Price in USD"),
    )

    is_active = models.BooleanField(
        default=True,
        verbose_name=_("Is active"),
        help_text=_("Is service currently offered"),
    )

    def __str__(self) -> str:
        """String representation of the lead."""

        return f"Product(pk={self.pk}, name={self.name})"

    @property
    def short_description(self) -> Any:
        """Returns shortened description for preview purposes.

        Returns:
            str: First 50 characters of description + '...' if exists,
                 otherwise 'No description' placeholder.
        """

        if not self.description:
            return _("No description")
        return (
            f"{self.description[:50]}..."
            if len(self.description) > 50
            else self.description
        )

    def get_absolute_url(self) -> Any:
        """Returns the absolute URL of the object."""

        return reverse("products:detail", kwargs={"pk": self.pk})
