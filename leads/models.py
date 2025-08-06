from typing import Any

from django.core.validators import validate_email
from django.db import models
from django.urls import reverse
from django.utils.translation import gettext_lazy as _

from crm.models import BaseModel


class Lead(BaseModel):
    """Represents a potential customer (lead) in the CRM system.

    Attributes:
        first_name (str): Lead's first name (100 chars max).
        last_name (str): Lead's last name (100 chars max).
        middle_name (str|None): Optional middle name (100 chars max).
        phone (str): Contact phone number (20 chars max, unique).
        email (str): Email address (validated, unique).
        advertisement (Advertisement|None): Related ad campaign (optional).

    Methods:
        get_absolute_url(): Returns URL for lead detail view.
    """

    class Meta:
        """Metadata options for the Lead model."""

        verbose_name = _("Lead")
        verbose_name_plural = _("Leads")
        ordering = ["-created_at"]
        indexes = [
            models.Index(fields=["last_name", "first_name"], name="lead_name_idx"),
            models.Index(fields=["email"], name="lead_email_idx"),
            models.Index(fields=["created_at"], name="lead_created_at_idx"),
        ]

    first_name = models.CharField(
        max_length=100,
        verbose_name=_("First name"),
        help_text=_("The lead's first name (max 100 characters)"),
    )
    last_name = models.CharField(
        max_length=100,
        verbose_name=_("Last name"),
        help_text=_("The lead's last name (max 100 characters)"),
    )
    middle_name = models.CharField(
        max_length=100,
        blank=True,
        null=True,
        verbose_name=_("Middle name"),
        help_text=_("The lead's middle name (optional, max 100 characters)"),
    )
    phone = models.CharField(
        max_length=20,
        unique=True,
        verbose_name=_("Phone number"),
        help_text=_("Contact phone number (max 20 characters)"),
    )
    email = models.EmailField(
        validators=[validate_email],
        unique=True,
        verbose_name=_("Email"),
        help_text=_("Valid email address"),
    )
    advertisement = models.ForeignKey(
        "advertisements.Advertisement",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="leads",
        verbose_name=_("Advertisement"),
        help_text=_("Related advertisement campaign (optional)"),
    )

    def __str__(self) -> str:
        """String representation of the lead."""

        return f"Lead(pk={self.pk}, surname={self.last_name}, name={self.first_name})"

    def get_absolute_url(self) -> Any:
        """Returns the absolute URL of the object."""

        return reverse("leads_detail", kwargs={"pk": self.pk})
