from django.db import models
from django.utils.translation import gettext_lazy as _


class BaseModel(models.Model):
    """Abstract base model with common fields and methods.

    Provides:
    - created_at (DateTime): When the instance was created
    - updated_at (DateTime): When the instance was last updated
    """

    class Meta:
        abstract = True

    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name=_("Created at"),
        help_text=_("When the %(class)s was created"),  # Placeholder
    )

    updated_at = models.DateTimeField(
        auto_now=True,
        verbose_name=_("Updated at"),
        help_text=_("When the %(class)s was last updated"),  # Placeholder
    )
