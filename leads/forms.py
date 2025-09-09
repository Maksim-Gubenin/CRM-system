from django import forms
from django.utils.translation import gettext_lazy as _

from leads.models import Lead


class LeadForm(forms.ModelForm):
    """
    Form for creating and updating Lead instances.

    Provides validation and input fields for lead personal and contact information,
    including name, phone, email, and advertisement source.
    """

    class Meta:
        """
        Configuration class for creating and updating Lead instances.

        Attributes:
            model (Lead): The model class this form is associated with
            fields (tuple): Fields to include in the form
            labels (dict): Custom labels for form fields with translations
            help_texts (dict): Help text descriptions for each field with translations
        """

        model = Lead
        fields = (
            "first_name",
            "last_name",
            "middle_name",
            "phone",
            "email",
            "advertisement",
        )

        labels = {
            "first_name": _("First name"),
            "last_name": _("Last name"),
            "middle_name": _("Middle name"),
            "phone": _("Phone number"),
            "email": _("Email address"),
            "advertisement": _("Advertisement campaign"),
        }

        help_texts = {
            "middle_name": _("(optional)"),
            "advertisement": _("Select related advertisement campaign"),
        }
