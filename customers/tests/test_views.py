from django.contrib.auth.models import Permission
from django.contrib.contenttypes.models import ContentType
from django.test import TestCase
from django.urls import reverse

from crm.utils.factories import ContractFactory, LeadFactory, UserFactory
from customers.models import Customer
from customers.views import CustomersUpdateView


class CustomersListViewTest(TestCase):
    """Tests for CustomersListView functionality."""

    @classmethod
    def setUpTestData(cls) -> None:
        """Create test data for all test methods."""
        cls.customer1 = Customer.objects.create(
            lead=LeadFactory(), contract=ContractFactory()
        )
        cls.customer2 = Customer.objects.create(
            lead=LeadFactory(), contract=ContractFactory()
        )

        cls.user = UserFactory()
        content_type = ContentType.objects.get_for_model(Customer)
        permission = Permission.objects.get(
            codename="view_customer", content_type=content_type
        )
        cls.user.user_permissions.add(permission)

    def test_view_requires_permission(self) -> None:
        """Test that view requires proper permission."""
        unauthorized_user = UserFactory()
        self.client.force_login(unauthorized_user)

        response = self.client.get(reverse("customers:list"))
        self.assertEqual(response.status_code, 403)

    def test_view_with_permission(self) -> None:
        """Test that user with permission can access the view."""
        self.client.force_login(self.user)
        response = self.client.get(reverse("customers:list"))

        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "customers/customers-list.html")

    def test_context_contains_customers(self) -> None:
        """Test that context contains all customers."""
        self.client.force_login(self.user)
        response = self.client.get(reverse("customers:list"))

        customers_in_context = list(response.context["customers"])
        self.assertEqual(len(customers_in_context), 2)
        self.assertCountEqual(customers_in_context, [self.customer1, self.customer2])

    def test_ordering_by_created_at_desc(self) -> None:
        """Test that customers are ordered by created_at descending."""
        self.client.force_login(self.user)
        response = self.client.get(reverse("customers:list"))

        customers = list(response.context["customers"])
        self.assertEqual(customers[0], self.customer2)
        self.assertEqual(customers[1], self.customer1)

    def test_pagination(self) -> None:
        """Test that pagination works correctly."""
        for _ in range(25):
            Customer.objects.create(lead=LeadFactory(), contract=ContractFactory())

        self.client.force_login(self.user)
        response = self.client.get(reverse("customers:list"))

        self.assertTrue(response.context["is_paginated"])
        self.assertEqual(len(response.context["customers"]), 20)

    def test_context_object_name(self) -> None:
        """Test that context object name is correct."""
        self.client.force_login(self.user)
        response = self.client.get(reverse("customers:list"))
        self.assertIn("customers", response.context)


class CustomersDetailViewTest(TestCase):
    """Tests for CustomersDetailView functionality."""

    @classmethod
    def setUpTestData(cls) -> None:
        """Create test data for all test methods."""
        cls.customer = Customer.objects.create(
            lead=LeadFactory(), contract=ContractFactory()
        )

        cls.user = UserFactory()
        content_type = ContentType.objects.get_for_model(Customer)
        permission = Permission.objects.get(
            codename="view_customer", content_type=content_type
        )
        cls.user.user_permissions.add(permission)

    def test_view_requires_permission(self) -> None:
        """Test that view requires proper permission."""
        unauthorized_user = UserFactory()
        self.client.force_login(unauthorized_user)

        response = self.client.get(
            reverse("customers:detail", kwargs={"pk": self.customer.pk})
        )
        self.assertEqual(response.status_code, 403)

    def test_view_with_permission(self) -> None:
        """Test that user with permission can access the view."""
        self.client.force_login(self.user)
        response = self.client.get(
            reverse("customers:detail", kwargs={"pk": self.customer.pk})
        )

        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "customers/customers-detail.html")

    def test_context_contains_customer(self) -> None:
        """Test that context contains the correct customer."""
        self.client.force_login(self.user)
        response = self.client.get(
            reverse("customers:detail", kwargs={"pk": self.customer.pk})
        )

        self.assertEqual(response.context["object"], self.customer)
        self.assertEqual(response.context["customer"], self.customer)

    def test_nonexistent_customer_returns_404(self) -> None:
        """Test that non-existent customer returns 404."""
        self.client.force_login(self.user)
        response = self.client.get(reverse("customers:detail", kwargs={"pk": 999}))
        self.assertEqual(response.status_code, 404)


class CustomersUpdateViewTest(TestCase):
    """Tests for CustomersUpdateView functionality."""

    @classmethod
    def setUpTestData(cls) -> None:
        """Create test data for all test methods."""
        cls.customer = Customer.objects.create(
            lead=LeadFactory(), contract=ContractFactory()
        )

        cls.new_lead = LeadFactory()
        cls.new_contract = ContractFactory()

        cls.user = UserFactory()
        content_type = ContentType.objects.get_for_model(Customer)
        permission = Permission.objects.get(
            codename="change_customer", content_type=content_type
        )
        cls.user.user_permissions.add(permission)

        cls.valid_data = {"lead": cls.new_lead.pk, "contract": cls.new_contract.pk}

    def test_view_requires_permission(self) -> None:
        """Test that view requires proper permission."""
        unauthorized_user = UserFactory()
        self.client.force_login(unauthorized_user)

        response = self.client.get(
            reverse("customers:update", kwargs={"pk": self.customer.pk})
        )
        self.assertEqual(response.status_code, 403)

    def test_view_with_permission(self) -> None:
        """Test that user with permission can access the view."""
        self.client.force_login(self.user)
        response = self.client.get(
            reverse("customers:update", kwargs={"pk": self.customer.pk})
        )

        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "customers/customers-update.html")

    def test_update_customer_valid_data(self) -> None:
        """Test successful customer update with valid data."""
        self.client.force_login(self.user)
        response = self.client.post(
            reverse("customers:update", kwargs={"pk": self.customer.pk}),
            data=self.valid_data,
        )

        self.assertEqual(response.status_code, 302)

        updated_customer = Customer.objects.get(pk=self.customer.pk)
        self.assertEqual(updated_customer.lead, self.new_lead)
        self.assertEqual(updated_customer.contract, self.new_contract)

    def test_get_success_url(self) -> None:
        """Test that success URL redirects to detail view."""
        self.client.force_login(self.user)
        view = CustomersUpdateView()
        view.object = self.customer

        success_url = view.get_success_url()
        self.assertEqual(success_url, self.customer.get_absolute_url())

    def test_nonexistent_customer_returns_404(self) -> None:
        """Test that non-existent customer returns 404."""
        self.client.force_login(self.user)
        response = self.client.get(reverse("customers:update", kwargs={"pk": 999}))
        self.assertEqual(response.status_code, 404)


class CustomersCreateViewTest(TestCase):
    """Tests for CustomersCreateView functionality."""

    @classmethod
    def setUpTestData(cls) -> None:
        """Create test data for all test methods."""
        cls.lead = LeadFactory()
        cls.contract = ContractFactory()

        cls.user = UserFactory()
        content_type = ContentType.objects.get_for_model(Customer)
        permission = Permission.objects.get(
            codename="add_customer", content_type=content_type
        )
        cls.user.user_permissions.add(permission)

        cls.valid_data = {"lead": cls.lead.pk, "contract": cls.contract.pk}

    def test_view_requires_permission(self) -> None:
        """Test that view requires proper permission."""
        unauthorized_user = UserFactory()
        self.client.force_login(unauthorized_user)

        response = self.client.get(reverse("customers:create"))
        self.assertEqual(response.status_code, 403)

    def test_view_with_permission(self) -> None:
        """Test that user with permission can access the view."""
        self.client.force_login(self.user)
        response = self.client.get(reverse("customers:create"))

        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "customers/customers-create.html")

    def test_create_customer_valid_data(self) -> None:
        """Test successful customer creation with valid data."""
        initial_count = Customer.objects.count()

        self.client.force_login(self.user)
        response = self.client.post(reverse("customers:create"), data=self.valid_data)

        self.assertEqual(response.status_code, 302)
        self.assertEqual(Customer.objects.count(), initial_count + 1)

        new_customer = Customer.objects.latest("created_at")
        self.assertEqual(new_customer.lead, self.lead)
        self.assertEqual(new_customer.contract, self.contract)

    def test_success_url_redirect(self) -> None:
        """Test that success URL redirects to list view."""
        self.client.force_login(self.user)
        response = self.client.post(reverse("customers:create"), data=self.valid_data)

        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, reverse("customers:list"))


class CustomersDeleteViewTest(TestCase):
    """Tests for CustomersDeleteView functionality."""

    @classmethod
    def setUpTestData(cls) -> None:
        """Create test data for all test methods."""
        cls.customer = Customer.objects.create(
            lead=LeadFactory(), contract=ContractFactory()
        )

        cls.user = UserFactory()
        content_type = ContentType.objects.get_for_model(Customer)
        permission = Permission.objects.get(
            codename="delete_customer", content_type=content_type
        )
        cls.user.user_permissions.add(permission)

    def test_view_requires_permission(self) -> None:
        """Test that view requires proper permission."""
        unauthorized_user = UserFactory()
        self.client.force_login(unauthorized_user)

        response = self.client.get(
            reverse("customers:delete", kwargs={"pk": self.customer.pk})
        )
        self.assertEqual(response.status_code, 403)

    def test_view_with_permission(self) -> None:
        """Test that user with permission can access the view."""
        self.client.force_login(self.user)
        response = self.client.get(
            reverse("customers:delete", kwargs={"pk": self.customer.pk})
        )

        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "customers/customers-delete.html")

    def test_delete_customer(self) -> None:
        """Test successful customer deletion."""
        self.client.force_login(self.user)

        self.assertTrue(Customer.objects.filter(pk=self.customer.pk).exists())

        response = self.client.post(
            reverse("customers:delete", kwargs={"pk": self.customer.pk})
        )

        self.assertEqual(response.status_code, 302)
        self.assertFalse(Customer.objects.filter(pk=self.customer.pk).exists())

    def test_success_url_redirect(self) -> None:
        """Test that success URL redirects to list view."""
        self.client.force_login(self.user)
        response = self.client.post(
            reverse("customers:delete", kwargs={"pk": self.customer.pk})
        )

        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, reverse("customers:list"))

    def test_nonexistent_customer_returns_404(self) -> None:
        """Test that non-existent customer returns 404."""
        self.client.force_login(self.user)
        response = self.client.get(reverse("customers:delete", kwargs={"pk": 999}))
        self.assertEqual(response.status_code, 404)
