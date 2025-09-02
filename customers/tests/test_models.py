from django.core.exceptions import ValidationError
from django.db import models
from django.test import TestCase
from django.urls import reverse
from django.utils.translation import gettext_lazy as _

from crm.utils.factories import ContractFactory, LeadFactory
from customers.models import Customer


class CustomerModelTest(TestCase):
    """Tests for Customer model functionality.

    Attributes:
        customer (Customer): Customer instance for testing
        lead (Lead): Lead instance for testing
        contract (Contract): Contract instance for testing
    """

    @classmethod
    def setUpTestData(cls) -> None:
        """Create test data for all test methods."""
        cls.lead = LeadFactory()
        cls.contract = ContractFactory()
        cls.customer = Customer.objects.create(lead=cls.lead, contract=cls.contract)

    def test_model_str_representation(self) -> None:
        """Test string representation of Customer model."""
        expected_str = f"Customer(pk={self.customer.pk})"
        self.assertEqual(str(self.customer), expected_str)

    def test_verbose_name(self) -> None:
        """Test verbose name configuration."""
        self.assertEqual(Customer._meta.verbose_name, _("Customer"))
        self.assertEqual(Customer._meta.verbose_name_plural, _("Customers"))

    def test_ordering(self) -> None:
        """Test model ordering configuration."""
        self.assertEqual(Customer._meta.ordering, ["-created_at"])

    def test_lead_field(self) -> None:
        """Test lead field configuration."""
        field = Customer._meta.get_field("lead")
        self.assertEqual(field.verbose_name, _("Lead"))
        self.assertEqual(field.remote_field.on_delete, models.PROTECT)
        self.assertEqual(field.remote_field.related_name, "customer")
        self.assertIsNotNone(field.help_text)
        self.assertTrue(field.one_to_one)

    def test_contract_field(self) -> None:
        """Test contract field configuration."""
        field = Customer._meta.get_field("contract")
        self.assertEqual(field.verbose_name, _("Contract"))
        self.assertEqual(field.remote_field.on_delete, models.PROTECT)
        self.assertEqual(field.remote_field.related_name, "customer")
        self.assertIsNotNone(field.help_text)
        self.assertTrue(field.one_to_one)

    def test_get_absolute_url(self) -> None:
        """Test get_absolute_url method returns correct URL."""
        expected_url = reverse("customers:detail", kwargs={"pk": self.customer.pk})
        self.assertEqual(self.customer.get_absolute_url(), expected_url)

    def test_lead_uniqueness(self) -> None:
        """Test lead uniqueness validation."""
        with self.assertRaises(ValidationError):
            customer_with_same_lead = Customer(
                lead=self.lead, contract=ContractFactory()
            )
            customer_with_same_lead.full_clean()

    def test_contract_uniqueness(self) -> None:
        """Test contract uniqueness validation."""
        with self.assertRaises(ValidationError):
            customer_with_same_contract = Customer(
                lead=LeadFactory(), contract=self.contract
            )
            customer_with_same_contract.full_clean()

    def test_lead_protection_on_delete(self) -> None:
        """Test that lead is protected from deletion when referenced by customer."""
        with self.assertRaises(Exception):
            self.lead.delete()

    def test_contract_protection_on_delete(self) -> None:
        """Test that contract is protected from deletion when referenced by customer."""
        with self.assertRaises(Exception):
            self.contract.delete()

    def test_created_at_updated_at_auto_now(self) -> None:
        """Test that created_at and updated_at fields are automatically managed."""
        customer = Customer.objects.create(
            lead=LeadFactory(), contract=ContractFactory()
        )
        self.assertIsNotNone(customer.created_at)
        self.assertIsNotNone(customer.updated_at)

    def test_lead_reverse_relationship(self) -> None:
        """Test reverse relationship from lead to customer."""
        self.assertEqual(self.lead.customer, self.customer)

    def test_contract_reverse_relationship(self) -> None:
        """Test reverse relationship from contract to customer."""
        self.assertEqual(self.contract.customer, self.customer)


class CustomerManagerTest(TestCase):
    """Tests for Customer model manager functionality.

    Attributes:
        customers (List[Customer]): List of customer instances
    """

    @classmethod
    def setUpTestData(cls) -> None:
        """Create test data for all test methods."""
        cls.customers = [
            Customer.objects.create(lead=LeadFactory(), contract=ContractFactory()),
            Customer.objects.create(lead=LeadFactory(), contract=ContractFactory()),
            Customer.objects.create(lead=LeadFactory(), contract=ContractFactory()),
        ]

    def test_default_manager_returns_all_customers(self) -> None:
        """Test that default manager returns all customers."""
        all_customers = Customer.objects.all()
        self.assertEqual(all_customers.count(), 3)
        for customer in self.customers:
            self.assertIn(customer, all_customers)

    def test_ordering_by_created_at_desc(self) -> None:
        """Test that customers are ordered by created_at descending."""
        customers = list(Customer.objects.all())
        self.assertEqual(customers[0], self.customers[2])
        self.assertEqual(customers[1], self.customers[1])
        self.assertEqual(customers[2], self.customers[0])
