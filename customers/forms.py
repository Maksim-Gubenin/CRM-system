from typing import Any

from django import forms
from django.utils.translation import gettext_lazy as _

from contracts.models import Contract
from customers.models import Customer
from leads.models import Lead


class CustomerForm(forms.ModelForm):
    """
    Form for creating and updating Customer instances.

    Provides fields and validation for customer data including
    lead selection and contract association with filtering of available options.
    """

    class Meta:
        """
        Configuration class for creating and updating Customer instances.

        Attributes:
            model (Customer): The model class this form is associated with
            fields (tuple): Fields to include in the form
            labels (dict): Custom labels for form fields
            help_texts (dict): Help text descriptions for each field
        """

        model = Customer
        fields = (
            "lead",
            "contract",
        )

        labels = {
            "lead": _("Lead"),
            "contract": _("Contract"),
        }

        help_texts = {
            "lead": _("Select a lead to convert to customer (only available leads are shown)"),
            "contract": _("Select a contract for the customer (only available contracts are shown)"),
        }

    def __init__(self, *args: Any, **kwargs: Any) -> None:
        """
        Initialize form with filtered querysets for lead and contract fields.

        Filters:
        - leads: Only leads that are not already converted to customers
        - contracts: Only contracts that are not already assigned to customers

        Args:
            *args: Variable length argument list
            **kwargs: Arbitrary keyword arguments
        """

        super().__init__(*args, **kwargs)
        self.fields["lead"].queryset = Lead.objects.filter(customer=None)
        self.fields["contract"].queryset = Contract.objects.filter(customer=None)
