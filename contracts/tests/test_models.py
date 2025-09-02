from datetime import date
from decimal import Decimal

from django.core.exceptions import ValidationError
from django.core.files.uploadedfile import SimpleUploadedFile
from django.db import models
from django.test import TestCase
from django.urls import reverse
from django.utils import timezone
from django.utils.translation import gettext_lazy as _

from contracts.models import Contract
from crm.utils.factories import ContractFactory, ProductFactory


class ContractModelTest(TestCase):
    """Tests for Contract model functionality.

    Attributes:
        contract (Contract): Contract instance for testing
        product (Product): Product instance for testing
    """

    @classmethod
    def setUpTestData(cls) -> None:
        """Create test data for all test methods."""
        cls.product = ProductFactory()
        cls.contract = ContractFactory(product=cls.product)

    def test_model_str_representation(self) -> None:
        """Test string representation of Contract model."""
        expected_str = f"Contract(pk={self.contract.pk}, name={self.contract.name})"
        self.assertEqual(str(self.contract), expected_str)

    def test_verbose_name(self) -> None:
        """Test verbose name configuration."""
        self.assertEqual(Contract._meta.verbose_name, _("Contract"))
        self.assertEqual(Contract._meta.verbose_name_plural, _("Contracts"))

    def test_ordering(self) -> None:
        """Test model ordering configuration."""
        self.assertEqual(Contract._meta.ordering, ["-cost"])

    def test_name_field(self) -> None:
        """Test name field configuration."""
        name_field = Contract._meta.get_field("name")
        self.assertEqual(name_field.max_length, 255)
        self.assertEqual(name_field.verbose_name, _("Contract name"))
        self.assertIsNotNone(name_field.help_text)

    def test_product_field(self) -> None:
        """Test product field configuration."""
        product_field = Contract._meta.get_field("product")
        self.assertEqual(product_field.verbose_name, _("Product"))
        self.assertEqual(product_field.remote_field.on_delete, models.PROTECT)
        self.assertIsNotNone(product_field.help_text)

    def test_document_field(self) -> None:
        """Test document field configuration."""
        document_field = Contract._meta.get_field("document")
        self.assertEqual(document_field.upload_to, "contracts/%Y/%m/")
        self.assertEqual(document_field.verbose_name, _("Document"))
        self.assertIsNotNone(document_field.help_text)
        self.assertEqual(len(document_field.validators), 1)

    def test_start_date_field(self) -> None:
        """Test start_date field configuration."""
        start_date_field = Contract._meta.get_field("start_date")
        self.assertEqual(start_date_field.verbose_name, _("Start date"))
        self.assertIsNotNone(start_date_field.help_text)

    def test_end_date_field(self) -> None:
        """Test end_date field configuration."""
        end_date_field = Contract._meta.get_field("end_date")
        self.assertEqual(end_date_field.verbose_name, _("End date"))
        self.assertIsNotNone(end_date_field.help_text)

    def test_cost_field(self) -> None:
        """Test cost field configuration."""
        cost_field = Contract._meta.get_field("cost")
        self.assertEqual(cost_field.max_digits, 12)
        self.assertEqual(cost_field.decimal_places, 2)
        self.assertEqual(cost_field.verbose_name, _("Cost"))
        self.assertIsNotNone(cost_field.help_text)

    def test_clean_method_valid_dates(self) -> None:
        """Test clean method with valid dates."""
        contract = ContractFactory(
            start_date=date(2024, 1, 1), end_date=date(2024, 12, 31)
        )

        try:
            contract.clean()
        except ValidationError:
            self.fail("clean() raised ValidationError unexpectedly!")

    def test_clean_method_invalid_dates(self) -> None:
        """Test clean method with invalid dates (end_date before start_date)."""
        contract = ContractFactory(
            start_date=date(2024, 12, 31), end_date=date(2024, 1, 1)
        )

        with self.assertRaises(ValidationError) as context:
            contract.clean()

        error_message = str(_("End date cannot be earlier than start date"))
        self.assertIn(error_message, str(context.exception))

    def test_get_absolute_url(self) -> None:
        """Test get_absolute_url method returns correct URL."""
        expected_url = reverse("contracts:detail", kwargs={"pk": self.contract.pk})
        self.assertEqual(self.contract.get_absolute_url(), expected_url)

    def test_cost_validation_positive_value(self) -> None:
        """Test cost validation with positive value."""
        contract = ContractFactory(cost=Decimal("1000.00"))
        contract.full_clean()

    def test_cost_validation_zero_value(self) -> None:
        """Test cost validation with zero value."""
        contract = ContractFactory(cost=Decimal("0.00"))
        contract.full_clean()

    def test_cost_validation_negative_value(self) -> None:
        """Test cost validation with negative value."""
        contract = ContractFactory(cost=Decimal("-100.00"))

        with self.assertRaises(ValidationError) as context:
            contract.full_clean()

        self.assertIn("cost", str(context.exception).lower())

    def test_document_file_extension_validation(self) -> None:
        """Test document file extension validation."""

        contract = ContractFactory()
        contract.document = SimpleUploadedFile(
            "contract.pdf", b"file_content", content_type="application/pdf"
        )
        contract.full_clean()

    def test_created_at_and_updated_at_fields(self) -> None:
        """Test that created_at and updated_at fields are automatically managed."""

        contract = ContractFactory()
        self.assertIsNotNone(contract.created_at)
        self.assertIsNotNone(contract.updated_at)
        self.assertTrue(contract.created_at <= timezone.now())
        self.assertTrue(contract.updated_at <= timezone.now())


class ContractManagerTest(TestCase):
    """Tests for Contract model manager functionality."""

    @classmethod
    def setUpTestData(cls) -> None:
        """Create test data for all test methods."""
        cls.contracts = ContractFactory.create_batch(5)

    def test_default_manager_returns_all_contracts(self) -> None:
        """Test that default manager returns all contracts."""
        all_contracts = Contract.objects.all()
        self.assertEqual(all_contracts.count(), 5)

    def test_contracts_have_required_fields(self) -> None:
        """Test that contracts have all required fields populated."""
        contracts = Contract.objects.all()

        for contract in contracts:
            self.assertIsNotNone(contract.name)
            self.assertIsNotNone(contract.product)
            self.assertIsNotNone(contract.document)
            self.assertIsNotNone(contract.start_date)
            self.assertIsNotNone(contract.end_date)
            self.assertIsNotNone(contract.cost)
            self.assertIsNotNone(contract.created_at)
            self.assertIsNotNone(contract.updated_at)
