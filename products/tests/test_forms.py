from django import forms
from django.test import TestCase

from products.forms import ProductForm
from products.models import Product


class ProductFormTest(TestCase):
    """Tests for the ProductForm validation and functionality.

    Attributes:
        valid_data (dict): Dictionary containing valid form data for testing
    """

    def setUp(self) -> None:
        """Initialize test data."""
        self.valid_data = {
            "name": "Test Product",
            "description": "Test description",
            "cost": 100.00,
        }

    def test_form_with_valid_data(self) -> None:
        """Test that form is valid with correct input data."""
        form = ProductForm(data=self.valid_data)
        self.assertTrue(form.is_valid())

    def test_form_with_empty_name(self) -> None:
        """Test that form is invalid when name field is empty."""
        invalid_data = self.valid_data.copy()
        invalid_data["name"] = ""
        form = ProductForm(data=invalid_data)
        self.assertFalse(form.is_valid())
        self.assertIn("name", form.errors)

    def test_form_with_negative_cost(self) -> None:
        """Test that form is invalid when cost is negative."""
        invalid_data = self.valid_data.copy()
        invalid_data["cost"] = -10
        form = ProductForm(data=invalid_data)
        self.assertFalse(form.is_valid())
        self.assertIn("cost", form.errors)

    def test_form_save(self) -> None:
        """Test that form.save() creates a new Product instance."""
        form = ProductForm(data=self.valid_data)
        if form.is_valid():
            product = form.save()
            self.assertEqual(product.name, "Test Product")
            self.assertEqual(product.cost, 100.00)
            self.assertTrue(Product.objects.filter(name="Test Product").exists())

    def test_form_fields(self) -> None:
        """Test that form contains expected fields with correct types."""
        form = ProductForm()
        self.assertIn("name", form.fields)
        self.assertIn("description", form.fields)
        self.assertIn("cost", form.fields)
        self.assertIsInstance(form.fields["cost"], forms.DecimalField)
