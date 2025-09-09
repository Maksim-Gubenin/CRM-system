from django.core.exceptions import ValidationError
from django.test import TestCase
from django.urls import reverse
from django.utils.translation import gettext_lazy as _

from advertisements.models import Advertisement
from crm.models import BaseModel
from crm.utils.factories import AdvertisementFactory, ProductFactory
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


class ProductModelAdditionalTests(TestCase):
    """Additional tests for Product model to achieve full coverage."""

    @classmethod
    def setUpTestData(cls) -> None:
        """Create test data once for all test methods."""
        cls.product = ProductFactory()

    def test_active_advertisements_count_with_active_ads(self) -> None:
        """Test active_advertisements_count method with active advertisements."""
        AdvertisementFactory.create_batch(2, product=self.product, is_active=True)
        AdvertisementFactory.create_batch(3, product=self.product, is_active=False)

        count = self.product.active_advertisements_count()
        self.assertEqual(count, 2)

    def test_active_advertisements_count_with_no_ads(self) -> None:
        """Test active_advertisements_count method with no advertisements."""
        product = ProductFactory()
        count = product.active_advertisements_count()
        self.assertEqual(count, 0)

    def test_active_advertisements_count_only_counts_own_ads(self) -> None:
        """Test that active_advertisements_count only counts ads for this product."""
        other_product = ProductFactory()
        AdvertisementFactory.create_batch(2, product=other_product, is_active=True)

        AdvertisementFactory.create_batch(1, product=self.product, is_active=True)

        count = self.product.active_advertisements_count()
        self.assertEqual(count, 1)

    def test_model_inheritance(self) -> None:
        """Test that Product inherits from BaseModel."""
        self.assertTrue(issubclass(Product, BaseModel))
        self.assertTrue(hasattr(self.product, "created_at"))
        self.assertTrue(hasattr(self.product, "updated_at"))

    def test_field_help_texts(self) -> None:
        """Test that all fields have help text."""
        fields_to_check = ["name", "description", "cost", "is_active"]

        for field_name in fields_to_check:
            field = Product._meta.get_field(field_name)
            self.assertIsNotNone(field.help_text)
            self.assertNotEqual(field.help_text.strip(), "")

    def test_field_verbose_names_translation(self) -> None:
        """Test that verbose names are properly translated."""
        field_verbose_names = {
            "name": _("Name"),
            "description": _("Description"),
            "cost": _("Cost"),
            "is_active": _("Is active"),
        }

        for field_name, expected_verbose_name in field_verbose_names.items():
            field = Product._meta.get_field(field_name)
            self.assertEqual(field.verbose_name, expected_verbose_name)


class ProductEdgeCaseTests(TestCase):
    """Tests for edge cases and boundary conditions."""

    def test_cost_zero_value(self) -> None:
        """Test that cost can be zero."""
        product = ProductFactory.build(cost=0)
        try:
            product.full_clean()
        except ValidationError:
            self.fail("Zero cost should be valid")

    def test_cost_large_value(self) -> None:
        """Test cost field with maximum allowed value."""
        max_value = 99999999.99
        product = ProductFactory.build(cost=max_value)
        try:
            product.full_clean()
        except ValidationError:
            self.fail("Maximum cost value should be valid")

    def test_name_max_length(self) -> None:
        """Test name field with maximum length."""
        max_name = "a" * 255
        product = ProductFactory.build(name=max_name)
        try:
            product.full_clean()
        except ValidationError:
            self.fail("Maximum length name should be valid")

    def test_name_too_long(self) -> None:
        """Test name field validation with too long value."""
        too_long_name = "a" * 256
        product = ProductFactory.build(name=too_long_name)
        with self.assertRaises(ValidationError):
            product.full_clean()

    def test_empty_description(self) -> None:
        """Test with empty string description."""
        product = ProductFactory.build(description="")
        self.assertEqual(product.short_description, _("No description"))


class ProductManagerEdgeCasesTest(TestCase):
    """Edge case tests for Product manager."""

    def test_manager_with_no_products(self) -> None:
        """Test manager methods when no products exist."""
        Product.objects.all().delete()
        self.assertEqual(Product.objects.count(), 0)
        self.assertEqual(list(Product.objects.all()), [])


class ProductAdvertisementRelationshipTest(TestCase):
    """Tests for the relationship between Product and Advertisement."""

    def test_advertisement_relationship(self) -> None:
        """Test that product has access to related advertisements."""
        product = ProductFactory()

        advertisements = AdvertisementFactory.create_batch(3, product=product)

        related_ads = product.advertisement_set.all()
        self.assertEqual(related_ads.count(), 3)
        for ad in advertisements:
            self.assertIn(ad, related_ads)

    def test_advertisement_cascade_delete(self) -> None:
        """Test what happens to advertisements when product is deleted."""
        product = ProductFactory()
        AdvertisementFactory.create_batch(2, product=product)

        ad_ids = list(product.advertisement_set.values_list("id", flat=True))

        product.delete()

        remaining_ads = Advertisement.objects.filter(id__in=ad_ids)
        self.assertEqual(remaining_ads.count(), 0)
