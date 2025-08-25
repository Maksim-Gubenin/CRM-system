from typing import Any

from django import forms
from django.utils.translation import gettext_lazy as _

from advertisements.models import Advertisement
from products.models import Product


class ADSForm(forms.ModelForm):
    """
    Form for creating and updating Advertisement instances.

    Provides fields and validation for advertisement data including
    name, channel selection, cost, and product association.
    """

    class Meta:
        """
        Configuration class for creating and updating Advertisement instances.

        Attributes:
            model (Advertisement): The model class this form is associated with
            fields (tuple): Fields to include in the form
            labels (dict): Custom labels for form fields
            help_texts (dict): Help text descriptions for each field
        """

        model = Advertisement
        fields = (
            "name",
            "channel",
            "cost",
            "product",
        )

        labels = {
            "name": _("Name"),
            "channel": _("Channel"),
            "cost": _("Price"),
            "product": _("Product"),
        }

        help_texts = {
            "name": _("Enter the Advertisement name"),
            "channel": _("Indicate the promotion channel"),
            "cost": _("Enter price in USD"),
            "product": _("Select a product/service for an advertising campaign"),
        }

    def __init__(self, *args: Any, **kwargs: Any) -> None:
        """
        Initialize form with filtered product queryset.
        """

        super().__init__(*args, **kwargs)
        self.fields["product"].queryset = Product.objects.filter(is_active=True)
