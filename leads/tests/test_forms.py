from django import forms
from django.test import TestCase

from crm.utils.factories import AdvertisementFactory, LeadFactory
from leads.forms import LeadForm
from leads.models import Lead


class LeadFormTest(TestCase):
    """Tests for LeadForm functionality.

    Attributes:
        advertisement (Advertisement): Advertisement instance for testing
        valid_data (Dict): Valid form data
        invalid_data (Dict): Invalid form data
    """

    @classmethod
    def setUpTestData(cls) -> None:
        """Create test data for all test methods."""
        cls.advertisement = AdvertisementFactory()

        cls.valid_data = {
            "first_name": "John",
            "last_name": "Doe",
            "middle_name": "Michael",
            "phone": "+1234567890",
            "email": "john.doe@example.com",
            "advertisement": cls.advertisement.pk,
        }

        cls.invalid_data = {
            "first_name": "",
            "last_name": "",
            "phone": "123",
            "email": "invalid-email",
            "advertisement": cls.advertisement.pk,
        }

    def test_form_meta_configuration(self) -> None:
        """Test form Meta class configuration."""
        form = LeadForm()

        self.assertEqual(form.Meta.model, Lead)
        self.assertEqual(
            form.Meta.fields,
            (
                "first_name",
                "last_name",
                "middle_name",
                "phone",
                "email",
                "advertisement",
            ),
        )

    def test_form_labels(self) -> None:
        """Test form field labels."""
        form = LeadForm()

        self.assertEqual(form.fields["first_name"].label, "First name")
        self.assertEqual(form.fields["last_name"].label, "Last name")
        self.assertEqual(form.fields["middle_name"].label, "Middle name")
        self.assertEqual(form.fields["phone"].label, "Phone number")
        self.assertEqual(form.fields["email"].label, "Email address")
        self.assertEqual(form.fields["advertisement"].label, "Advertisement campaign")

    def test_form_help_texts(self) -> None:
        """Test form field help texts."""
        form = LeadForm()

        self.assertEqual(form.fields["first_name"].help_text, "")
        self.assertEqual(form.fields["last_name"].help_text, "")
        self.assertEqual(form.fields["middle_name"].help_text, "(optional)")
        self.assertEqual(form.fields["phone"].help_text, "")
        self.assertEqual(form.fields["email"].help_text, "")
        self.assertEqual(
            form.fields["advertisement"].help_text,
            "Select related advertisement campaign",
        )

    def test_form_fields_widgets(self) -> None:
        """Test form field widgets."""
        form = LeadForm()

        self.assertIsInstance(form.fields["first_name"].widget, forms.TextInput)
        self.assertIsInstance(form.fields["last_name"].widget, forms.TextInput)
        self.assertIsInstance(form.fields["middle_name"].widget, forms.TextInput)
        self.assertIsInstance(form.fields["phone"].widget, forms.TextInput)
        self.assertIsInstance(form.fields["email"].widget, forms.EmailInput)
        self.assertIsInstance(form.fields["advertisement"].widget, forms.Select)

    def test_form_with_valid_data(self) -> None:
        """Test form validation with valid data."""
        form = LeadForm(data=self.valid_data)

        self.assertTrue(form.is_valid())
        self.assertEqual(len(form.errors), 0)

    def test_form_with_invalid_data(self) -> None:
        """Test form validation with invalid data."""
        form = LeadForm(data=self.invalid_data)

        self.assertFalse(form.is_valid())
        self.assertIn("first_name", form.errors)
        self.assertIn("last_name", form.errors)
        self.assertIn("email", form.errors)

    def test_form_with_empty_first_name(self) -> None:
        """Test form validation with empty first name."""
        data = self.valid_data.copy()
        data["first_name"] = ""

        form = LeadForm(data=data)
        self.assertFalse(form.is_valid())
        self.assertIn("first_name", form.errors)

    def test_form_with_empty_last_name(self) -> None:
        """Test form validation with empty last name."""
        data = self.valid_data.copy()
        data["last_name"] = ""

        form = LeadForm(data=data)
        self.assertFalse(form.is_valid())
        self.assertIn("last_name", form.errors)

    def test_form_with_invalid_email(self) -> None:
        """Test form validation with invalid email."""
        data = self.valid_data.copy()
        data["email"] = "invalid-email"

        form = LeadForm(data=data)
        self.assertFalse(form.is_valid())
        self.assertIn("email", form.errors)

    def test_form_without_middle_name(self) -> None:
        """Test form validation without middle name."""
        data = self.valid_data.copy()
        data["middle_name"] = ""

        form = LeadForm(data=data)
        self.assertTrue(form.is_valid())

    def test_form_save_method(self) -> None:
        """Test form save method creates lead instance."""
        form = LeadForm(data=self.valid_data)

        self.assertTrue(form.is_valid())
        lead = form.save()

        self.assertIsInstance(lead, Lead)
        self.assertEqual(lead.first_name, "John")
        self.assertEqual(lead.last_name, "Doe")
        self.assertEqual(lead.email, "john.doe@example.com")

    def test_form_update_existing_instance(self) -> None:
        """Test form can update existing lead instance."""
        lead = LeadFactory()

        updated_data = self.valid_data.copy()
        updated_data["first_name"] = "Updated Name"

        form = LeadForm(data=updated_data, instance=lead)
        self.assertTrue(form.is_valid())

        updated_lead = form.save()
        self.assertEqual(updated_lead.first_name, "Updated Name")
        self.assertEqual(updated_lead.pk, lead.pk)

    def test_form_field_required_status(self) -> None:
        """Test that required fields are marked as required."""
        form = LeadForm()

        self.assertTrue(form.fields["first_name"].required)
        self.assertTrue(form.fields["last_name"].required)
        self.assertTrue(form.fields["phone"].required)
        self.assertTrue(form.fields["email"].required)
        self.assertTrue(form.fields["advertisement"].required)
        self.assertFalse(form.fields["middle_name"].required)

    def test_form_with_missing_required_fields(self) -> None:
        """Test form validation with missing required fields."""
        incomplete_data = {
            "first_name": "John",
            "last_name": "Doe",
        }

        form = LeadForm(data=incomplete_data)
        self.assertFalse(form.is_valid())
        self.assertIn("phone", form.errors)
        self.assertIn("email", form.errors)
        self.assertIn("advertisement", form.errors)

    def test_form_phone_uniqueness_validation(self) -> None:
        """Test form validation for phone uniqueness."""
        existing_lead = LeadFactory()

        data = self.valid_data.copy()
        data["phone"] = existing_lead.phone

        form = LeadForm(data=data)
        self.assertFalse(form.is_valid())
        self.assertIn("phone", form.errors)

    def test_form_email_uniqueness_validation(self) -> None:
        """Test form validation for email uniqueness."""
        existing_lead = LeadFactory()

        data = self.valid_data.copy()
        data["email"] = existing_lead.email

        form = LeadForm(data=data)
        self.assertFalse(form.is_valid())
        self.assertIn("email", form.errors)
