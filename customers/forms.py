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
            "lead": _("Select a lead (only available leads are shown)"),
            "contract": _("Select a contract (only available contracts are shown)"),
        }

    def __init__(self, *args: Any, **kwargs: Any) -> None:
        """
        Initialize form with filtered querysets for lead and contract fields.
        """
        super().__init__(*args, **kwargs)

        current_customer = self.instance if self.instance and self.instance.pk else None

        lead_queryset = Lead.objects.filter(customer=None)
        if current_customer and current_customer.lead:
            lead_queryset = lead_queryset | Lead.objects.filter(
                pk=current_customer.lead.pk
            )
        self.fields["lead"].queryset = lead_queryset

        contract_queryset = Contract.objects.filter(customer=None)
        if current_customer and current_customer.contract:
            contract_queryset = contract_queryset | Contract.objects.filter(
                pk=current_customer.contract.pk
            )
        self.fields["contract"].queryset = contract_queryset
