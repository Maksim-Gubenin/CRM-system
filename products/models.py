from typing import Any

from django.core.validators import MinValueValidator
from django.db import models
from django.urls import reverse
from django.utils.translation import gettext_lazy as _

from crm.models import BaseModel
from crm.cache import cache_method


class Product(BaseModel):
    """Represents a service or product with caching"""

    class Meta:
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

    @property
    def short_description(self) -> Any:
        """Returns shortened description for preview purposes"""
        if not self.description:
            return _("No description")
        return (
            f"{self.description[:50]}..."
            if len(self.description) > 50
            else self.description
        )

    @cache_method(timeout=600)
    def active_advertisements_count(self) -> int:
        """Count of active advertisements for this product"""
        print(f"📊 [ACTIVE ADS COUNT] Вычисляю для product_{self.pk}")
        return self.advertisement_set.filter(is_active=True).count()

    def get_absolute_url(self) -> Any:
        return reverse("products:detail", kwargs={"pk": self.pk})