from django import forms
from django.test import TestCase
from django.utils.translation import gettext as _

from advertisements.forms import ADSForm
from advertisements.models import Advertisement
from crm.utils.factories import AdvertisementFactory, ProductFactory
from products.models import Product


class ADSFormTest(TestCase):
    """Tests for ADSForm validation and functionality."""

    @classmethod
    def setUpTestData(cls) -> None:
        """Create test data for all test methods."""

        cls.active_product = ProductFactory(is_active=True)
        cls.inactive_product = ProductFactory(is_active=False)
        cls.valid_data = {
            "name": "Test Campaign",
            "channel": "social",
            "cost": 1000.00,
            "product": cls.active_product.pk,
        }

    def test_form_meta_configuration(self) -> None:
        """Test that form Meta class is properly configured."""

        form = ADSForm()

        self.assertEqual(form.Meta.model, Advertisement)

        expected_fields = (
            "name",
            "channel",
            "cost",
            "product",
        )
        self.assertEqual(form.Meta.fields, expected_fields)

        expected_labels = {
            "name": _("Name"),
            "channel": _("Channel"),
            "cost": _("Price"),
            "product": _("Product"),
        }
        self.assertEqual(form.Meta.labels, expected_labels)

        expected_help_texts = {
            "name": _("Enter the Advertisement name"),
            "channel": _("Indicate the promotion channel"),
            "cost": _("Enter price in USD"),
            "product": _("Select a product/service for an advertising campaign"),
        }
        self.assertEqual(form.Meta.help_texts, expected_help_texts)

    def test_form_with_valid_data(self) -> None:
        """Test that form is valid with correct input data."""

        form = ADSForm(data=self.valid_data)
        self.assertTrue(form.is_valid())

        advertisement = form.save()
        self.assertEqual(advertisement.name, "Test Campaign")
        self.assertEqual(advertisement.channel, "social")
        self.assertEqual(advertisement.cost, 1000.00)
        self.assertEqual(advertisement.product, self.active_product)

    def test_form_with_empty_name(self) -> None:
        """Test that form is invalid when name field is empty."""

        invalid_data = self.valid_data.copy()
        invalid_data["name"] = ""
        form = ADSForm(data=invalid_data)

        self.assertFalse(form.is_valid())
        self.assertIn("name", form.errors)
        self.assertEqual(form.errors["name"][0], "This field is required.")

    def test_form_with_long_name(self) -> None:
        """Test that form validates name field max length."""

        invalid_data = self.valid_data.copy()
        invalid_data["name"] = "A" * 256
        form = ADSForm(data=invalid_data)

        self.assertFalse(form.is_valid())
        self.assertIn("name", form.errors)

    def test_form_with_negative_cost(self) -> None:
        """Test that form is invalid when cost is negative."""

        invalid_data = self.valid_data.copy()
        invalid_data["cost"] = -100
        form = ADSForm(data=invalid_data)

        self.assertFalse(form.is_valid())
        self.assertIn("cost", form.errors)
        self.assertEqual(
            form.errors["cost"][0], "Ensure this value is greater than or equal to 0."
        )

    def test_form_with_zero_cost(self) -> None:
        """Test that form is valid when cost is zero."""

        valid_data = self.valid_data.copy()
        valid_data["cost"] = 0
        form = ADSForm(data=valid_data)

        self.assertTrue(form.is_valid())

    def test_form_with_invalid_channel(self) -> None:
        """Test that form is invalid with invalid channel choice."""

        invalid_data = self.valid_data.copy()
        invalid_data["channel"] = "invalid_channel"
        form = ADSForm(data=invalid_data)

        self.assertFalse(form.is_valid())
        self.assertIn("channel", form.errors)

    def test_form_with_valid_channel_choices(self) -> None:
        """Test that form accepts all valid channel choices."""

        valid_channels = ["social", "search", "context", "email", "other"]

        for channel in valid_channels:
            with self.subTest(channel=channel):
                valid_data = self.valid_data.copy()
                valid_data["channel"] = channel
                form = ADSForm(data=valid_data)
                self.assertTrue(form.is_valid())

    def test_form_without_product(self) -> None:
        """Test that form is invalid when product is not selected."""

        invalid_data = self.valid_data.copy()
        invalid_data["product"] = ""
        form = ADSForm(data=invalid_data)

        self.assertFalse(form.is_valid())
        self.assertIn("product", form.errors)

    def test_form_with_nonexistent_product(self) -> None:
        """Test that form is invalid with non-existent product ID."""

        invalid_data = self.valid_data.copy()
        invalid_data["product"] = 9999
        form = ADSForm(data=invalid_data)

        self.assertFalse(form.is_valid())
        self.assertIn("product", form.errors)

    def test_form_product_queryset_filtering(self) -> None:
        """Test that product queryset is filtered to active products only."""

        form = ADSForm()

        product_queryset = form.fields["product"].queryset
        active_products = Product.objects.filter(is_active=True)

        self.assertEqual(set(product_queryset), set(active_products))
        self.assertNotIn(self.inactive_product, product_queryset)
        self.assertIn(self.active_product, product_queryset)

    def test_form_field_types(self) -> None:
        """Test that form contains expected fields with correct types."""

        form = ADSForm()

        self.assertIn("name", form.fields)
        self.assertIsInstance(form.fields["name"], forms.CharField)

        self.assertIn("channel", form.fields)
        self.assertIsInstance(form.fields["channel"], forms.ChoiceField)

        self.assertIn("cost", form.fields)
        self.assertIsInstance(form.fields["cost"], forms.DecimalField)

        self.assertIn("product", form.fields)
        self.assertIsInstance(form.fields["product"], forms.ModelChoiceField)

    def test_form_save_creates_instance(self) -> None:
        """Test that form.save() creates a new Advertisement instance."""

        form = ADSForm(data=self.valid_data)

        self.assertTrue(form.is_valid())

        initial_count = Advertisement.objects.count()

        advertisement = form.save()

        self.assertEqual(Advertisement.objects.count(), initial_count + 1)
        self.assertEqual(advertisement.name, "Test Campaign")
        self.assertTrue(Advertisement.objects.filter(name="Test Campaign").exists())

    def test_form_save_updates_existing_instance(self) -> None:
        """Test that form.save() updates an existing Advertisement instance."""

        existing_ad = AdvertisementFactory()

        update_data = self.valid_data.copy()
        update_data["name"] = "Updated Campaign"

        form = ADSForm(data=update_data, instance=existing_ad)

        self.assertTrue(form.is_valid())

        initial_count = Advertisement.objects.count()
        updated_ad = form.save()

        self.assertEqual(Advertisement.objects.count(), initial_count)
        self.assertEqual(updated_ad.name, "Updated Campaign")
        self.assertEqual(updated_ad.pk, existing_ad.pk)

    def test_form_initialization_with_custom_args(self) -> None:
        """Test that form initialization works with custom arguments."""

        initial_data = {"name": "Pre-filled Campaign"}
        form = ADSForm(initial=initial_data)

        self.assertEqual(form.initial["name"], "Pre-filled Campaign")

        instance = AdvertisementFactory(name="Existing Campaign")
        form = ADSForm(instance=instance)

        self.assertEqual(form.instance.name, "Existing Campaign")

    def test_form_clean_method(self) -> None:
        """Test form cleaning and validation."""
        form = ADSForm(data=self.valid_data)

        self.assertTrue(form.is_valid())
        cleaned_data = form.clean()

        self.assertEqual(cleaned_data["name"], "Test Campaign")
        self.assertEqual(cleaned_data["channel"], "social")
        self.assertEqual(cleaned_data["cost"], 1000.00)
        self.assertEqual(cleaned_data["product"], self.active_product)
