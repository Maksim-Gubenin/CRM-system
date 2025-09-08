from django.test import TestCase

from crm.utils.factories import ContractFactory, CustomerFactory, LeadFactory
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

    def test_form_init_with_none_instance(self) -> None:
        """Test form initialization with None instance."""
        form = CustomerForm(instance=None)
        self.assertIsNotNone(form)
        self.assertEqual(form.fields["lead"].queryset.count(), 1)
        self.assertEqual(form.fields["contract"].queryset.count(), 1)

    def test_form_init_with_new_instance_no_pk(self) -> None:
        """Test form initialization with new instance (no pk)."""
        new_customer = Customer(lead=None, contract=None)
        form = CustomerForm(instance=new_customer)

        self.assertEqual(form.fields["lead"].queryset.count(), 1)
        self.assertEqual(form.fields["contract"].queryset.count(), 1)
        self.assertIn(self.available_lead, form.fields["lead"].queryset)
        self.assertIn(self.available_contract, form.fields["contract"].queryset)

    def test_form_with_current_assigned_objects_during_update(self) -> None:
        """Test that form allows keeping currently assigned objects during update."""
        form_data = {
            "lead": self.taken_lead.pk,
            "contract": self.taken_contract.pk,
        }
        form = CustomerForm(data=form_data, instance=self.existing_customer)

        self.assertTrue(form.is_valid(), form.errors)
        updated_customer = form.save()

        self.assertEqual(updated_customer.lead, self.taken_lead)
        self.assertEqual(updated_customer.contract, self.taken_contract)


class CustomerFormEdgeCasesTest(TestCase):
    """Test edge cases for CustomerForm."""

    def test_multiple_available_objects(self) -> None:
        """Test form with multiple available objects."""
        lead1 = LeadFactory()
        lead2 = LeadFactory()
        contract1 = ContractFactory()
        contract2 = ContractFactory()

        form = CustomerForm()

        self.assertEqual(form.fields["lead"].queryset.count(), 2)
        self.assertEqual(form.fields["contract"].queryset.count(), 2)
        self.assertIn(lead1, form.fields["lead"].queryset)
        self.assertIn(lead2, form.fields["lead"].queryset)
        self.assertIn(contract1, form.fields["contract"].queryset)
        self.assertIn(contract2, form.fields["contract"].queryset)

    def test_no_available_objects(self) -> None:
        """Test form when no objects are available."""
        lead = LeadFactory()
        contract = ContractFactory()
        CustomerFactory(lead=lead, contract=contract)

        form = CustomerForm()

        self.assertEqual(form.fields["lead"].queryset.count(), 0)
        self.assertEqual(form.fields["contract"].queryset.count(), 0)

    def test_form_with_existing_customer_and_available_objects(self) -> None:
        """Test form with existing customer when other objects become available."""
        customer = CustomerFactory()

        available_lead = LeadFactory()
        available_contract = ContractFactory()

        form = CustomerForm(instance=customer)

        self.assertEqual(form.fields["lead"].queryset.count(), 2)
        self.assertEqual(form.fields["contract"].queryset.count(), 2)
        self.assertIn(customer.lead, form.fields["lead"].queryset)
        self.assertIn(available_lead, form.fields["lead"].queryset)
        self.assertIn(customer.contract, form.fields["contract"].queryset)
        self.assertIn(available_contract, form.fields["contract"].queryset)


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

    def test_form_queryset_filtering_after_creation(self) -> None:
        """Test that form properly filters querysets after customer creation."""

        lead1 = LeadFactory()
        lead2 = LeadFactory()
        contract1 = ContractFactory()
        contract2 = ContractFactory()

        CustomerFactory(lead=lead1, contract=contract1)

        form = CustomerForm()

        self.assertEqual(form.fields["lead"].queryset.count(), 1)
        self.assertEqual(form.fields["contract"].queryset.count(), 1)
        self.assertIn(lead2, form.fields["lead"].queryset)
        self.assertIn(contract2, form.fields["contract"].queryset)
        self.assertNotIn(lead1, form.fields["lead"].queryset)
        self.assertNotIn(contract1, form.fields["contract"].queryset)
