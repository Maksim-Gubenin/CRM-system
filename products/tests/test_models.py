from django.core.exceptions import ValidationError
from django.test import TestCase
from django.urls import reverse
from django.utils.translation import gettext_lazy as _

from crm.utils.factories import ProductFactory
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

    def test_verbose_name(self) -> None:
        """Test verbose name configuration."""
        self.assertEqual(Product._meta.verbose_name, _("Product"))
        self.assertEqual(Product._meta.verbose_name_plural, _("Products"))

    def test_ordering(self) -> None:
        """Test model ordering configuration."""
        self.assertEqual(Product._meta.ordering, ["name"])

    def test_name_field(self) -> None:
        """Test name field configuration."""
        field = Product._meta.get_field("name")
        self.assertEqual(field.max_length, 255)
        self.assertEqual(field.verbose_name, _("Name"))
        self.assertIsNotNone(field.help_text)

    def test_description_field(self) -> None:
        """Test description field configuration."""
        field = Product._meta.get_field("description")
        self.assertEqual(field.verbose_name, _("Description"))
        self.assertTrue(field.blank)
        self.assertTrue(field.null)
        self.assertIsNotNone(field.help_text)

    def test_cost_field(self) -> None:
        """Test cost field configuration."""
        field = Product._meta.get_field("cost")
        self.assertEqual(field.max_digits, 10)
        self.assertEqual(field.decimal_places, 2)
        self.assertEqual(field.verbose_name, _("Cost"))
        self.assertIsNotNone(field.help_text)

    def test_is_active_field(self) -> None:
        """Test is_active field configuration."""
        field = Product._meta.get_field("is_active")
        self.assertEqual(field.verbose_name, _("Is active"))
        self.assertTrue(field.default)
        self.assertIsNotNone(field.help_text)

    def test_indexes_exist(self) -> None:
        """Test that database indexes are properly configured."""
        indexes = [index.name for index in Product._meta.indexes]
        expected_indexes = ["product_name_idx", "product_cost_idx"]
        for expected_index in expected_indexes:
            self.assertIn(expected_index, indexes)

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

        over_length = "b" * 51
        product = ProductFactory(description=over_length)
        self.assertEqual(product.short_description, "b" * 50 + "...")

    def test_get_absolute_url(self) -> None:
        """Test get_absolute_url method."""
        expected_url = reverse("products:detail", kwargs={"pk": self.product.pk})
        self.assertEqual(self.product.get_absolute_url(), expected_url)

    def test_cost_validation(self) -> None:
        """Test cost field validation."""
        product = ProductFactory.build(cost=-100)
        with self.assertRaises(ValidationError):
            product.full_clean()

    def test_created_at_updated_at_auto_now(self) -> None:
        """Test that created_at and updated_at fields are automatically managed."""
        product = ProductFactory()
        self.assertIsNotNone(product.created_at)
        self.assertIsNotNone(product.updated_at)


class ProductManagerTest(TestCase):
    """Tests for Product model manager functionality.

    Attributes:
        active_products (List[Product]): List of active product instances
        inactive_products (List[Product]): List of inactive product instances
    """

    @classmethod
    def setUpTestData(cls) -> None:
        """Create test data for all test methods."""
        cls.active_products = ProductFactory.create_batch(3, is_active=True)
        cls.inactive_products = ProductFactory.create_batch(2, is_active=False)

    def test_default_manager_returns_all_products(self) -> None:
        """Test that default manager returns all products."""
        all_products = Product.objects.all()
        self.assertEqual(all_products.count(), 5)
        for product in self.active_products + self.inactive_products:
            self.assertIn(product, all_products)

    def test_ordering_by_name(self) -> None:
        """Test that products are ordered by name."""
        products = list(Product.objects.all())
        sorted_products = sorted(products, key=lambda x: x.name)
        self.assertEqual(products, sorted_products)
