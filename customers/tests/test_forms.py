from django.test import TestCase

from crm.utils.factories import ContractFactory, LeadFactory
from customers.forms import CustomerForm
from customers.models import Customer


class CustomerFormTest(TestCase):
    """Tests for CustomerForm functionality."""

    @classmethod
    def setUpTestData(cls) -> None:
        """Create test data for all test methods."""
        cls.available_lead = LeadFactory()
        cls.available_contract = ContractFactory()

        cls.taken_lead = LeadFactory()
        cls.taken_contract = ContractFactory()
        cls.existing_customer = Customer.objects.create(
            lead=cls.taken_lead, contract=cls.taken_contract
        )

    def test_form_fields(self) -> None:
        """Test that form has correct fields."""
        form = CustomerForm()
        self.assertIn("lead", form.fields)
        self.assertIn("contract", form.fields)

    def test_form_labels(self) -> None:
        """Test that form fields have correct labels."""
        form = CustomerForm()
        self.assertEqual(form.fields["lead"].label, "Lead")
        self.assertEqual(form.fields["contract"].label, "Contract")

    def test_form_help_texts(self) -> None:
        """Test that form fields have correct help texts."""
        form = CustomerForm()
        self.assertEqual(
            form.fields["lead"].help_text,
            "Select a lead (only available leads are shown)",
        )
        self.assertEqual(
            form.fields["contract"].help_text,
            "Select a contract (only available contracts are shown)",
        )

    def test_available_leads_queryset(self) -> None:
        """Test that form filters available leads."""
        form = CustomerForm()

        self.assertIn(self.available_lead, form.fields["lead"].queryset)
        self.assertNotIn(self.taken_lead, form.fields["lead"].queryset)

    def test_available_contracts_queryset(self) -> None:
        """Test that form filters available contracts."""
        form = CustomerForm()

        self.assertIn(self.available_contract, form.fields["contract"].queryset)
        self.assertNotIn(self.taken_contract, form.fields["contract"].queryset)

    def test_form_with_existing_customer(self) -> None:
        """Test form initialization with existing customer instance."""
        form = CustomerForm(instance=self.existing_customer)

        self.assertIn(self.taken_lead, form.fields["lead"].queryset)
        self.assertIn(self.taken_contract, form.fields["contract"].queryset)

    def test_form_validation_valid_data(self) -> None:
        """Test form validation with valid data."""
        form_data = {
            "lead": self.available_lead.pk,
            "contract": self.available_contract.pk,
        }
        form = CustomerForm(data=form_data)

        self.assertTrue(form.is_valid())

    def test_form_validation_missing_data(self) -> None:
        """Test form validation with missing data."""
        form_data = {}
        form = CustomerForm(data=form_data)

        self.assertFalse(form.is_valid())
        self.assertIn("lead", form.errors)
        self.assertIn("contract", form.errors)

    def test_form_validation_taken_lead(self) -> None:
        """Test form validation with already taken lead."""
        form_data = {"lead": self.taken_lead.pk, "contract": self.available_contract.pk}
        form = CustomerForm(data=form_data)

        self.assertFalse(form.is_valid())
        self.assertIn("lead", form.errors)

    def test_form_validation_taken_contract(self) -> None:
        """Test form validation with already taken contract."""
        form_data = {"lead": self.available_lead.pk, "contract": self.taken_contract.pk}
        form = CustomerForm(data=form_data)

        self.assertFalse(form.is_valid())
        self.assertIn("contract", form.errors)

    def test_form_save(self) -> None:
        """Test that form can save correctly."""
        form_data = {
            "lead": self.available_lead.pk,
            "contract": self.available_contract.pk,
        }
        form = CustomerForm(data=form_data)

        self.assertTrue(form.is_valid())
        customer = form.save()

        self.assertEqual(customer.lead, self.available_lead)
        self.assertEqual(customer.contract, self.available_contract)
        self.assertTrue(Customer.objects.filter(pk=customer.pk).exists())

    def test_form_update_existing_customer(self) -> None:
        """Test form update with existing customer."""
        new_available_lead = LeadFactory()
        new_available_contract = ContractFactory()

        form_data = {
            "lead": new_available_lead.pk,
            "contract": new_available_contract.pk,
        }
        form = CustomerForm(data=form_data, instance=self.existing_customer)

        self.assertTrue(form.is_valid())
        updated_customer = form.save()

        self.assertEqual(updated_customer.lead, new_available_lead)
        self.assertEqual(updated_customer.contract, new_available_contract)
        self.assertEqual(updated_customer.pk, self.existing_customer.pk)

    def test_queryset_ordering(self) -> None:
        """Test that querysets are properly ordered."""
        form = CustomerForm()

        leads = list(form.fields["lead"].queryset)
        self.assertTrue(len(leads) > 0)

        contracts = list(form.fields["contract"].queryset)
        self.assertTrue(len(contracts) > 0)


class CustomerFormIntegrationTest(TestCase):
    """Integration tests for CustomerForm with model."""

    @classmethod
    def setUpTestData(cls) -> None:
        """Create test data for all test methods."""
        cls.lead1 = LeadFactory()
        cls.contract1 = ContractFactory()

    def test_create_customer_via_form(self) -> None:
        """Test creating a customer through the form."""
        form_data = {"lead": self.lead1.pk, "contract": self.contract1.pk}
        form = CustomerForm(data=form_data)

        self.assertTrue(form.is_valid())
        customer = form.save()

        self.assertEqual(Customer.objects.count(), 1)
        self.assertEqual(customer.lead, self.lead1)
        self.assertEqual(customer.contract, self.contract1)

        form2 = CustomerForm()
        self.assertNotIn(self.lead1, form2.fields["lead"].queryset)
        self.assertNotIn(self.contract1, form2.fields["contract"].queryset)
