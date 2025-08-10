from django import forms

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
        fields = (
            "name",
            "description",
            "cost",
        )
