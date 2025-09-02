from django.core.exceptions import ValidationError
from django.db import models
from django.test import TestCase
from django.urls import reverse
from django.utils.translation import gettext_lazy as _

from crm.utils.factories import AdvertisementFactory, LeadFactory
from leads.models import Lead


class LeadModelTest(TestCase):
    """Tests for Lead model functionality.

    Attributes:
        lead (Lead): Lead instance for testing
        advertisement (Advertisement): Advertisement instance for testing
    """

    @classmethod
    def setUpTestData(cls) -> None:
        """Create test data for all test methods."""
        cls.lead = LeadFactory()
        cls.advertisement = AdvertisementFactory()

    def test_model_str_representation(self) -> None:
        """Test string representation of Lead model."""
        expected_str = (
            f"Lead(pk={self.lead.pk}, "
            f"surname={self.lead.last_name}, "
            f"name={self.lead.first_name})"
        )
        self.assertEqual(str(self.lead), expected_str)

    def test_verbose_name(self) -> None:
        """Test verbose name configuration."""
        self.assertEqual(Lead._meta.verbose_name, _("Lead"))
        self.assertEqual(Lead._meta.verbose_name_plural, _("Leads"))

    def test_ordering(self) -> None:
        """Test model ordering configuration."""
        self.assertEqual(Lead._meta.ordering, ["-created_at"])

    def test_first_name_field(self) -> None:
        """Test first_name field configuration."""
        field = Lead._meta.get_field("first_name")
        self.assertEqual(field.max_length, 100)
        self.assertEqual(field.verbose_name, _("First name"))
        self.assertIsNotNone(field.help_text)

    def test_last_name_field(self) -> None:
        """Test last_name field configuration."""
        field = Lead._meta.get_field("last_name")
        self.assertEqual(field.max_length, 100)
        self.assertEqual(field.verbose_name, _("Last name"))
        self.assertIsNotNone(field.help_text)

    def test_middle_name_field(self) -> None:
        """Test middle_name field configuration."""
        field = Lead._meta.get_field("middle_name")
        self.assertEqual(field.max_length, 100)
        self.assertEqual(field.verbose_name, _("Middle name"))
        self.assertTrue(field.blank)
        self.assertTrue(field.null)
        self.assertIsNotNone(field.help_text)

    def test_phone_field(self) -> None:
        """Test phone field configuration."""
        field = Lead._meta.get_field("phone")
        self.assertEqual(field.max_length, 20)
        self.assertEqual(field.verbose_name, _("Phone number"))
        self.assertTrue(field.unique)
        self.assertIsNotNone(field.help_text)

    def test_email_field(self) -> None:
        """Test email field configuration."""
        field = Lead._meta.get_field("email")
        self.assertEqual(field.verbose_name, _("Email"))
        self.assertTrue(field.unique)
        self.assertEqual(len(field.validators), 1)
        self.assertIsNotNone(field.help_text)

    def test_advertisement_field(self) -> None:
        """Test advertisement field configuration."""
        field = Lead._meta.get_field("advertisement")
        self.assertEqual(field.verbose_name, _("Advertisement"))
        self.assertEqual(field.remote_field.on_delete, models.PROTECT)
        self.assertEqual(field.remote_field.related_name, "leads")
        self.assertIsNotNone(field.help_text)

    def test_get_absolute_url(self) -> None:
        """Test get_absolute_url method returns correct URL."""
        expected_url = reverse("leads:detail", kwargs={"pk": self.lead.pk})
        self.assertEqual(self.lead.get_absolute_url(), expected_url)

    def test_phone_uniqueness(self) -> None:
        """Test phone number uniqueness validation."""
        with self.assertRaises(ValidationError):
            lead_with_same_phone = LeadFactory(phone=self.lead.phone)
            lead_with_same_phone.full_clean()

    def test_email_uniqueness(self) -> None:
        """Test email uniqueness validation."""
        with self.assertRaises(ValidationError):
            lead_with_same_email = LeadFactory(email=self.lead.email)
            lead_with_same_email.full_clean()

    def test_email_validation(self) -> None:
        """Test email format validation."""
        invalid_lead = LeadFactory.build(email="invalid-email")
        with self.assertRaises(ValidationError):
            invalid_lead.full_clean()

    def test_middle_name_optional(self) -> None:
        """Test that middle name field is optional."""
        lead_without_middle_name = LeadFactory(middle_name=None)
        lead_without_middle_name.full_clean()

    def test_indexes_exist(self) -> None:
        """Test that database indexes are properly configured."""
        indexes = [index.name for index in Lead._meta.indexes]
        expected_indexes = ["lead_name_idx", "lead_email_idx", "lead_created_at_idx"]
        for expected_index in expected_indexes:
            self.assertIn(expected_index, indexes)

    def test_created_at_updated_at_auto_now(self) -> None:
        """Test that created_at and updated_at fields are automatically managed."""
        lead = LeadFactory()
        self.assertIsNotNone(lead.created_at)
        self.assertIsNotNone(lead.updated_at)


class LeadManagerTest(TestCase):
    """Tests for Lead model manager functionality.

    Attributes:
        active_leads (List[Lead]): List of active lead instances
        inactive_leads (List[Lead]): List of inactive lead instances
    """

    @classmethod
    def setUpTestData(cls) -> None:
        """Create test data for all test methods."""
        cls.active_leads = LeadFactory.create_batch(3)
        cls.inactive_leads = LeadFactory.create_batch(2, is_active=False)

    def test_active_manager_returns_only_active_leads(self) -> None:
        """Test that active manager returns only active leads."""
        active_leads = Lead.active.all()
        self.assertEqual(active_leads.count(), 3)
        for lead in active_leads:
            self.assertTrue(lead.is_active)

    def test_active_manager_excludes_inactive_leads(self) -> None:
        """Test that active manager excludes inactive leads."""
        active_leads = Lead.active.all()
        for lead in self.inactive_leads:
            self.assertNotIn(lead, active_leads)
