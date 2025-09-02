from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import TestCase

from contracts.forms import ContractForm
from contracts.models import Contract
from crm.utils.factories import ProductFactory


class ContractFormTest(TestCase):
    """Tests for ContractForm functionality."""

    @classmethod
    def setUpTestData(cls) -> None:
        """Create test data for all test methods."""
        cls.product = ProductFactory()

        cls.valid_data = {
            "name": "CONTRACT-2024-001",
            "product": cls.product.pk,
            "start_date": "2024-01-01",
            "end_date": "2024-12-31",
            "cost": "10000.00",
        }

    def test_form_meta_configuration(self) -> None:
        """Test form Meta class configuration."""
        form = ContractForm()

        self.assertEqual(form.Meta.model, Contract)
        self.assertEqual(
            form.Meta.fields,
            ("name", "product", "document", "start_date", "end_date", "cost"),
        )

    def test_form_with_valid_data_and_document(self) -> None:
        """Test form validation with valid data and document."""
        document = SimpleUploadedFile(
            "contract.pdf", b"file_content", content_type="application/pdf"
        )

        form = ContractForm(data=self.valid_data, files={"document": document})
        self.assertTrue(form.is_valid())
        self.assertEqual(len(form.errors), 0)

    def test_form_without_document(self) -> None:
        """Test form validation fails without document."""
        form = ContractForm(data=self.valid_data)
        self.assertFalse(form.is_valid())
        self.assertIn("document", form.errors)

    def test_form_with_invalid_document_extension(self) -> None:
        """Test form validation with invalid document extension."""
        document = SimpleUploadedFile(
            "contract.txt", b"file_content", content_type="text/plain"
        )

        form = ContractForm(data=self.valid_data, files={"document": document})
        self.assertFalse(form.is_valid())
        self.assertIn("document", form.errors)

    def test_form_with_valid_word_document(self) -> None:
        """Test form validation with valid Word document."""
        document = SimpleUploadedFile(
            "contract.doc", b"file_content", content_type="application/msword"
        )

        form = ContractForm(data=self.valid_data, files={"document": document})
        self.assertTrue(form.is_valid())

    def test_form_product_queryset_filtering(self) -> None:
        """Test that product queryset is filtered to active products only."""
        inactive_product = ProductFactory(is_active=False)

        form = ContractForm()

        self.assertNotIn(inactive_product, form.fields["product"].queryset)

    def test_form_save_method(self) -> None:
        """Test form save method creates contract instance."""
        document = SimpleUploadedFile(
            "contract.pdf", b"file_content", content_type="application/pdf"
        )

        form = ContractForm(data=self.valid_data, files={"document": document})
        self.assertTrue(form.is_valid())

        contract = form.save()
        self.assertIsInstance(contract, Contract)
        self.assertEqual(contract.name, "CONTRACT-2024-001")
        self.assertEqual(contract.cost, 10000.00)
        self.assertIsNotNone(contract.document)

    def test_form_field_required_status(self) -> None:
        """Test that required fields are marked as required."""
        form = ContractForm()

        self.assertTrue(form.fields["name"].required)
        self.assertTrue(form.fields["product"].required)
        self.assertTrue(form.fields["document"].required)
        self.assertTrue(form.fields["start_date"].required)
        self.assertTrue(form.fields["end_date"].required)
        self.assertTrue(form.fields["cost"].required)
