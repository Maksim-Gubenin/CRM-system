from django import forms
from django.utils.translation import gettext_lazy as _

from leads.models import Lead


class LeadForm(forms.ModelForm):
    """
    """

    class Meta:
        """
        """

        model = Lead
        fields = ("first_name", "last_name", "middle_name", "phone", "email", "advertisement")

        # labels = {
        #     "name": _("Name"),
        #     "description": _("Description"),
        #     "cos": _("Price"),
        # }

        # help_texts = {
        #     "name": _("Enter the product/service name"),
        #     "description": _("Enter detailed description"),
        #     "cost": _("Enter price in USD"),
        # }
