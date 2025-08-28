from django import forms
from django.utils.translation import gettext_lazy as _

from products.models import Product


class ProductForm(forms.ModelForm):
    """
    Form for creating and updating Product instances.
    """

    class Meta:
        """
        Configuration class for creating and updating Products instances.

        Attributes:
            model (Product): The model class this form is associated with
            fields (tuple): Fields to include in the form
        """

        model = Product
        fields = ("name", "description", "cost")

        labels = {
            "name": _("Name"),
            "description": _("Description"),
            "cost": _("Price"),
        }

        help_texts = {
            "name": _("Enter the product/service name"),
            "description": _("Enter detailed description"),
            "cost": _("Enter price in USD"),
        }
