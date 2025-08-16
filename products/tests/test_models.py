from django.core.exceptions import ValidationError
from django.test import TestCase
from django.utils.translation import gettext as _

from crm.utils import ProductFactory
from products.models import Product


class ProductModelTest(TestCase):
    """Tests for Product model functionality.

    Attributes:
        product (Product): Product instance for testing
        long_description (str): Long description text for testing
        short_description (str): Short description text for testing
    """

    @classmethod
    def setUpTestData(cls) -> None:
        """Create test data once for all test methods."""
        cls.product = ProductFactory()
        cls.long_description = (
            "Lorem ipsum dolor sit amet, consectetur adipiscing elit. " * 3
        )
        cls.short_description = "Short description"

    def test_string_representation(self) -> None:
        """Test the string representation of the model."""
        self.assertEqual(
            str(self.product),
            f"Product(pk={self.product.pk}, name={self.product.name})",
        )

    def test_short_description_with_none(self) -> None:
        """Test short_description property when description is None."""
        product = ProductFactory(description=None)
        self.assertEqual(product.short_description, _("No description"))

    def test_short_description_with_short_text(self) -> None:
        """Test short_description with text shorter than 50 characters."""
        product = ProductFactory(description=self.short_description)
        self.assertEqual(product.short_description, self.short_description)

    def test_short_description_with_long_text(self) -> None:
        """Test short_description with text longer than 50 characters."""
        product = ProductFactory(description=self.long_description)
        expected = self.long_description[:50] + "..."
        self.assertEqual(product.short_description, expected)
        self.assertEqual(len(product.short_description), 53)

    def test_short_description_edge_cases(self) -> None:
        """Test edge cases for short_description property."""
        exact_length = "a" * 50
        product = ProductFactory(description=exact_length)
        self.assertEqual(product.short_description, exact_length)

        # Boundary + 1 character
        over_length = "b" * 51
        product = ProductFactory(description=over_length)
        self.assertEqual(product.short_description, "b" * 50 + "...")

    def test_model_meta_options(self) -> None:
        """Test model Meta options."""
        meta = Product._meta
        self.assertEqual(meta.verbose_name, _("Product"))
        self.assertEqual(meta.verbose_name_plural, _("Products"))
        self.assertEqual(meta.ordering, ["name"])

    def test_get_absolute_url(self) -> None:
        """Test get_absolute_url method."""
        url = self.product.get_absolute_url()
        self.assertEqual(url, f"/products/{self.product.pk}/")

    def test_cost_validation(self) -> None:
        """Test cost field validation."""
        product = ProductFactory.build(cost=-100)
        with self.assertRaises(ValidationError):
            product.full_clean()
