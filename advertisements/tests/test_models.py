from django.core.exceptions import ValidationError
from django.test import TestCase
from django.utils.translation import activate
from django.utils.translation import gettext as _

from advertisements.models import Advertisement
from crm.utils.factories import (
    AdvertisementFactory,
    ContractFactory,
    CustomerFactory,
    LeadFactory,
    ProductFactory,
)


class AdvertisementModelTest(TestCase):
    """Tests for Advertisement model functionality."""

    @classmethod
    def setUpTestData(cls) -> None:
        """Create test data once for all test methods."""
        cls.product = ProductFactory()
        cls.advertisement = AdvertisementFactory(product=cls.product)

    def test_string_representation(self) -> None:
        """Test the string representation of the model."""
        expected = (
            f"Ad(pk={self.advertisement.pk}, name={self.advertisement.name[:20]})"
        )
        self.assertEqual(str(self.advertisement), expected)

    def test_model_meta_options(self) -> None:
        """Test model Meta options."""
        meta = Advertisement._meta
        self.assertEqual(meta.verbose_name, _("Advertisement"))
        self.assertEqual(meta.verbose_name_plural, _("Advertisements"))
        self.assertEqual(meta.ordering, ["-cost"])

    def test_get_absolute_url(self) -> None:
        """Test get_absolute_url method."""
        activate("en-us")
        url = self.advertisement.get_absolute_url()
        self.assertTrue(url.endswith(f"/ads/{self.advertisement.pk}/"))

    def test_cost_validation_negative(self) -> None:
        """Test cost field validation with negative value."""
        ad = AdvertisementFactory.build(cost=-100, product=self.product)
        with self.assertRaises(ValidationError):
            ad.full_clean()

    def test_cost_validation_zero(self) -> None:
        """Test cost field validation with zero value."""
        ad = AdvertisementFactory.build(cost=0, product=self.product)
        try:
            ad.full_clean()
        except ValidationError:
            self.fail("Zero cost should be valid")

    def test_cost_validation_positive(self) -> None:
        """Test cost field validation with positive value."""
        ad = AdvertisementFactory.build(cost=100.50, product=self.product)
        try:
            ad.full_clean()
        except ValidationError:
            self.fail("Positive cost should be valid")

    def test_channel_choices(self) -> None:
        """Test that channel field accepts only valid choices."""
        valid_channels = ["social", "search", "context", "email", "other"]

        for channel in valid_channels:
            ad = AdvertisementFactory.build(channel=channel, product=self.product)
            try:
                ad.full_clean()
            except ValidationError:
                self.fail(f"Channel {channel} should be valid")

    def test_invalid_channel(self) -> None:
        """Test that invalid channel raises validation error."""
        ad = AdvertisementFactory.build(channel="invalid_channel", product=self.product)
        with self.assertRaises(ValidationError):
            ad.full_clean()

    def test_leads_count_method(self) -> None:
        """Test leads_count method."""
        LeadFactory.create_batch(3, advertisement=self.advertisement)

        self.assertEqual(self.advertisement.leads_count(), 3)

    def test_leads_count_empty(self) -> None:
        """Test leads_count method with no leads."""
        self.assertEqual(self.advertisement.leads_count(), 0)

    def test_customers_count_method(self) -> None:
        """Test customers_count method."""

        leads = LeadFactory.create_batch(4, advertisement=self.advertisement)

        CustomerFactory(lead=leads[0])
        CustomerFactory(lead=leads[1])

        self.assertEqual(self.advertisement.customers_count(), 2)

    def test_customers_count_empty(self) -> None:
        """Test customers_count method with no customers."""
        self.assertEqual(self.advertisement.customers_count(), 0)

    def test_conversion_rate_method(self) -> None:
        """Test conversion_rate method."""

        leads = LeadFactory.create_batch(4, advertisement=self.advertisement)
        CustomerFactory(lead=leads[0])
        CustomerFactory(lead=leads[1])

        self.assertEqual(self.advertisement.conversion_rate(), 0.5)

    def test_conversion_rate_zero_leads(self) -> None:
        """Test conversion_rate method with no leads."""
        self.assertEqual(self.advertisement.conversion_rate(), 0.0)

    def test_conversion_rate_zero_customers(self) -> None:
        """Test conversion_rate method with leads but no customers."""
        LeadFactory.create_batch(3, advertisement=self.advertisement)
        self.assertEqual(self.advertisement.conversion_rate(), 0.0)

    def test_profit_method_with_income(self) -> None:
        """Test profit method with actual income."""

        ad = AdvertisementFactory(cost=1000, product=self.product)

        lead = LeadFactory(advertisement=ad)
        contract = ContractFactory(cost=3000)
        CustomerFactory(lead=lead, contract=contract)

        # ROI = 3000 / 1000 = 3.0
        self.assertEqual(ad.profit(), 3.0)

    def test_profit_method_no_income(self) -> None:
        """Test profit method with no income."""
        ad = AdvertisementFactory(cost=1000, product=self.product)
        self.assertIsNone(ad.profit())

    def test_profit_method_zero_cost(self) -> None:
        """Test profit method with zero cost."""
        ad = AdvertisementFactory(cost=0, product=self.product)
        self.assertIsNone(ad.profit())

    def test_is_active_default(self) -> None:
        """Test that is_active defaults to True."""
        ad = Advertisement(
            product=self.product, name="Test", channel="social", cost=100
        )
        self.assertTrue(ad.is_active)

    def test_product_relationship(self) -> None:
        """Test the relationship with Product model."""
        self.assertEqual(self.advertisement.product, self.product)
        self.assertIn(self.advertisement, self.product.advertisement_set.all())

    def test_verbose_names(self) -> None:
        """Test verbose names of fields."""
        field_verbose_names = {
            "name": _("Campaign name"),
            "channel": _("Advertising channel"),
            "cost": _("Budget"),
            "product": _("Product"),
            "is_active": _("Active"),
        }

        for field, expected_verbose in field_verbose_names.items():
            with self.subTest(field=field):
                self.assertEqual(
                    Advertisement._meta.get_field(field).verbose_name, expected_verbose
                )
