from typing import Any

from django.db import models
from django.utils.translation import gettext_lazy as _

from crm.cache import ModelCacheMixin


class BaseModel(models.Model, ModelCacheMixin):
    """Abstract base model with common fields, methods and caching capabilities.

    Provides:
    - created_at (DateTime): Timestamp when the instance was created
    - updated_at (DateTime): Timestamp when the instance was last updated
    - Automatic caching functionality with ModelCacheMixin integration
    - Consistent save/delete behavior with cache management

    Attributes:
        created_at: Auto-set datetime when object is created
        updated_at: Auto-updated datetime when object is modified
    """

    class Meta:
        abstract = True

    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name=_("Created at"),
        help_text=_("When the %(class)s was created"),
    )

    updated_at = models.DateTimeField(
        auto_now=True,
        verbose_name=_("Updated at"),
        help_text=_("When the %(class)s was last updated"),
    )

    def save(self, *args: Any, **kwargs: Any) -> None:
        """Override save method to handle caching operations.

        Args:
            *args: Positional arguments for parent save method
            **kwargs: Keyword arguments for parent save method

        Returns:
            The result of the parent save method
        """
        is_new = self.pk is None

        super().save(*args, **kwargs)

        if not is_new:
            self.invalidate_cache()

        self.set_cache()

    def delete(self, *args: Any, **kwargs: Any) -> Any:
        """Override delete method to handle cache invalidation.

        Args:
            *args: Positional arguments for parent delete method
            **kwargs: Keyword arguments for parent delete method

        Returns:
            The result of the parent delete method
        """
        self.invalidate_cache()

        return super().delete(*args, **kwargs)
