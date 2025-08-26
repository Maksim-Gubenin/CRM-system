from typing import Any

from django import forms
from django.utils.translation import gettext_lazy as _

from contracts.models import Contract
from products.models import Product


class ContractForm(forms.ModelForm):
    """
    Form for creating and updating Contract instances.

    Provides fields and validation for contract data including
    name, product selection, document upload, dates, and cost.
    """

    class Meta:
        """
        Configuration class for creating and updating Contract instances.

        Attributes:
            model (Contract): The model class this form is associated with
            fields (tuple): Fields to include in the form
            labels (dict): Custom labels for form fields with translations
            help_texts (dict): Help text descriptions for each field with translations
        """

        model = Contract
        fields = (
            "name",
            "product",
            "document",
            "start_date",
            "end_date",
            "cost",
        )

        labels = {
            "name": _("Contract name"),
            "product": _("Product"),
            "document": _("Document"),
            "start_date": _("Start date"),
            "end_date": _("End date"),
            "cost": _("Cost"),
        }

        help_texts = {
            "name": _("Official contract reference number/name"),
            "product": _("Service/product covered by this contract"),
            "document": _("Scanned contract file (PDF or Word)"),
            "start_date": _("Service start date"),
            "end_date": _("Service end date"),
            "cost": _("Total contract value"),
        }

    def __init__(self, *args: Any, **kwargs: Any) -> None:
        """
        Initialize form with filtered product queryset.

        Args:
            *args: Variable length argument list
            **kwargs: Arbitrary keyword arguments
        """

        super().__init__(*args, **kwargs)
        self.fields["product"].queryset = Product.objects.filter(is_active=True)
