from django.contrib.auth import get_user_model
from django.contrib.auth.models import Permission
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import TestCase
from django.urls import reverse

from contracts.forms import ContractForm
from contracts.models import Contract
from contracts.views import (
    ContractDeleteView,
    ContractsCreateView,
    ContractsDetailView,
    ContractsListView,
    ContractsUpdateView,
)
from crm.utils.factories import ContractFactory, ProductFactory, UserFactory

User = get_user_model()


class ContractsListViewTest(TestCase):
    """Tests for ContractsListView functionality.

    Attributes:
        contracts (List[Contract]): List of contract instances
        user_with_permission (User): User with view_contract permission
        user_without_permission (User): User without view_contract permission
        superuser (User): Superuser instance
    """

    @classmethod
    def setUpTestData(cls) -> None:
        """Create test data for all test methods."""
        cls.contracts = ContractFactory.create_batch(5)
        cls.superuser = UserFactory(is_superuser=True)

        cls.user_with_permission = UserFactory()
        view_permission = Permission.objects.get(codename="view_contract")
        cls.user_with_permission.user_permissions.add(view_permission)

        cls.user_without_permission = UserFactory()

    def test_view_configuration(self) -> None:
        """Test view class configuration."""
        view = ContractsListView()

        self.assertEqual(view.permission_required, "contracts.view_contract")
        self.assertEqual(view.template_name, "contracts/contracts-list.html")
        self.assertEqual(view.model, Contract)
        self.assertEqual(view.paginate_by, 20)
        self.assertEqual(view.context_object_name, "contracts")

    def test_view_requires_permission(self) -> None:
        """Test that view requires proper permission."""
        self.client.force_login(self.user_with_permission)
        response = self.client.get(reverse("contracts:list"))
        self.assertEqual(response.status_code, 200)

    def test_view_without_permission(self) -> None:
        """Test that view denies access without permission."""
        self.client.force_login(self.user_without_permission)
        response = self.client.get(reverse("contracts:list"))
        self.assertEqual(response.status_code, 403)

    def test_view_with_superuser(self) -> None:
        """Test that superuser can access the view."""
        self.client.force_login(self.superuser)
        response = self.client.get(reverse("contracts:list"))
        self.assertEqual(response.status_code, 200)

    def test_template_used(self) -> None:
        """Test that correct template is used."""
        self.client.force_login(self.user_with_permission)
        response = self.client.get(reverse("contracts:list"))
        self.assertTemplateUsed(response, "contracts/contracts-list.html")

    def test_context_contains_contracts(self) -> None:
        """Test that context contains contracts."""
        self.client.force_login(self.user_with_permission)
        response = self.client.get(reverse("contracts:list"))

        self.assertIn("contracts", response.context)
        self.assertEqual(len(response.context["contracts"]), 5)
        self.assertEqual(
            list(response.context["contracts"]), list(Contract.objects.all())
        )

    def test_pagination(self) -> None:
        """Test that pagination works correctly."""
        ContractFactory.create_batch(25)

        self.client.force_login(self.user_with_permission)
        response = self.client.get(reverse("contracts:list"))

        self.assertTrue(response.context["is_paginated"])
        self.assertEqual(len(response.context["contracts"]), 20)

    def test_ordering(self) -> None:
        """Test that contracts are ordered by cost descending."""
        self.client.force_login(self.user_with_permission)
        response = self.client.get(reverse("contracts:list"))

        contracts = response.context["contracts"]
        costs = [contract.cost for contract in contracts]
        self.assertEqual(costs, sorted(costs, reverse=True))


class ContractsDetailViewTest(TestCase):
    """Tests for ContractsDetailView functionality.

    Attributes:
        contract (Contract): Contract instance for testing
        user_with_permission (User): User with view_contract permission
        user_without_permission (User): User without view_contract permission
        superuser (User): Superuser instance
    """

    @classmethod
    def setUpTestData(cls) -> None:
        """Create test data for all test methods."""
        cls.contract = ContractFactory()
        cls.superuser = UserFactory(is_superuser=True)

        cls.user_with_permission = UserFactory()
        view_permission = Permission.objects.get(codename="view_contract")
        cls.user_with_permission.user_permissions.add(view_permission)

        cls.user_without_permission = UserFactory()

    def test_view_configuration(self) -> None:
        """Test view class configuration."""
        view = ContractsDetailView()

        self.assertEqual(view.permission_required, "contracts.view_contract")
        self.assertEqual(view.model, Contract)
        self.assertEqual(view.template_name, "contracts/contracts-detail.html")

    def test_view_requires_permission(self) -> None:
        """Test that view requires proper permission."""
        self.client.force_login(self.user_with_permission)
        response = self.client.get(
            reverse("contracts:detail", kwargs={"pk": self.contract.pk})
        )
        self.assertEqual(response.status_code, 200)

    def test_view_without_permission(self) -> None:
        """Test that view denies access without permission."""
        self.client.force_login(self.user_without_permission)
        response = self.client.get(
            reverse("contracts:detail", kwargs={"pk": self.contract.pk})
        )
        self.assertEqual(response.status_code, 403)

    def test_view_with_superuser(self) -> None:
        """Test that superuser can access the view."""
        self.client.force_login(self.superuser)
        response = self.client.get(
            reverse("contracts:detail", kwargs={"pk": self.contract.pk})
        )
        self.assertEqual(response.status_code, 200)

    def test_template_used(self) -> None:
        """Test that correct template is used."""
        self.client.force_login(self.user_with_permission)
        response = self.client.get(
            reverse("contracts:detail", kwargs={"pk": self.contract.pk})
        )
        self.assertTemplateUsed(response, "contracts/contracts-detail.html")

    def test_context_contains_contract(self) -> None:
        """Test that context contains the contract."""
        self.client.force_login(self.user_with_permission)
        response = self.client.get(
            reverse("contracts:detail", kwargs={"pk": self.contract.pk})
        )

        self.assertIn("object", response.context)
        self.assertIn("contract", response.context)
        self.assertEqual(response.context["object"], self.contract)
        self.assertEqual(response.context["contract"], self.contract)

    def test_nonexistent_contract(self) -> None:
        """Test view with non-existent contract ID."""
        self.client.force_login(self.user_with_permission)
        response = self.client.get(reverse("contracts:detail", kwargs={"pk": 9999}))
        self.assertEqual(response.status_code, 404)


class ContractsUpdateViewTest(TestCase):
    """Tests for ContractsUpdateView functionality.

    Attributes:
        contract (Contract): Contract instance for testing
        user_with_permission (User): User with change_contract permission
        user_without_permission (User): User without change_contract permission
        superuser (User): Superuser instance
        valid_data (Dict): Valid form data for update
    """

    @classmethod
    def setUpTestData(cls) -> None:
        """Create test data for all test methods."""
        cls.contract = ContractFactory()
        cls.superuser = UserFactory(is_superuser=True)

        cls.user_with_permission = UserFactory()
        change_permission = Permission.objects.get(codename="change_contract")
        cls.user_with_permission.user_permissions.add(change_permission)

        cls.user_without_permission = UserFactory()

        cls.valid_data = {
            "name": "Updated Contract Name",
            "product": cls.contract.product.pk,
            "start_date": cls.contract.start_date,
            "end_date": cls.contract.end_date,
            "cost": "1500.00",
        }

    def test_view_configuration(self) -> None:
        """Test view class configuration."""
        view = ContractsUpdateView()

        self.assertEqual(view.permission_required, "contracts.change_contract")
        self.assertEqual(view.model, Contract)
        self.assertEqual(view.template_name, "contracts/contracts-update.html")
        self.assertEqual(view.form_class, ContractForm)

    def test_view_requires_permission(self) -> None:
        """Test that view requires proper permission."""
        self.client.force_login(self.user_with_permission)
        response = self.client.get(
            reverse("contracts:update", kwargs={"pk": self.contract.pk})
        )
        self.assertEqual(response.status_code, 200)

    def test_view_without_permission(self) -> None:
        """Test that view denies access without permission."""
        self.client.force_login(self.user_without_permission)
        response = self.client.get(
            reverse("contracts:update", kwargs={"pk": self.contract.pk})
        )
        self.assertEqual(response.status_code, 403)

    def test_view_with_superuser(self) -> None:
        """Test that superuser can access the view."""
        self.client.force_login(self.superuser)
        response = self.client.get(
            reverse("contracts:update", kwargs={"pk": self.contract.pk})
        )
        self.assertEqual(response.status_code, 200)

    def test_template_used(self) -> None:
        """Test that correct template is used."""
        self.client.force_login(self.user_with_permission)
        response = self.client.get(
            reverse("contracts:update", kwargs={"pk": self.contract.pk})
        )
        self.assertTemplateUsed(response, "contracts/contracts-update.html")

    def test_context_contains_form(self) -> None:
        """Test that context contains form."""
        self.client.force_login(self.user_with_permission)
        response = self.client.get(
            reverse("contracts:update", kwargs={"pk": self.contract.pk})
        )

        self.assertIn("form", response.context)
        self.assertIsInstance(response.context["form"], ContractForm)

    def test_get_success_url_method(self) -> None:
        """Test get_success_url method returns correct URL."""
        view = ContractsUpdateView()
        view.object = self.contract

        expected_url = self.contract.get_absolute_url()
        self.assertEqual(view.get_success_url(), expected_url)

    def test_successful_update(self) -> None:
        """Test successful contract update."""
        self.client.force_login(self.superuser)

        response = self.client.post(
            reverse("contracts:update", kwargs={"pk": self.contract.pk}),
            data=self.valid_data,
        )

        self.assertEqual(response.status_code, 302)

        updated_contract = Contract.objects.get(pk=self.contract.pk)
        self.assertEqual(updated_contract.name, "Updated Contract Name")
        self.assertEqual(updated_contract.cost, 1500.00)

    def test_redirect_after_update(self) -> None:
        """Test redirect after successful update."""
        self.client.force_login(self.user_with_permission)
        self.client.force_login(self.superuser)

        response = self.client.post(
            reverse("contracts:update", kwargs={"pk": self.contract.pk}),
            data=self.valid_data,
        )

        self.assertRedirects(response, self.contract.get_absolute_url())


class ContractsCreateViewTest(TestCase):
    """Tests for ContractsCreateView functionality.

    Attributes:
        user_with_permission (User): User with add_contract permission
        user_without_permission (User): User without add_contract permission
        superuser (User): Superuser instance
        product (Product): Product instance for testing
        valid_data (Dict): Valid form data for creation
    """

    @classmethod
    def setUpTestData(cls) -> None:
        """Create test data for all test methods."""
        cls.product = ProductFactory()
        cls.superuser = UserFactory(is_superuser=True)

        cls.user_with_permission = UserFactory()
        add_permission = Permission.objects.get(codename="add_contract")
        cls.user_with_permission.user_permissions.add(add_permission)

        cls.user_without_permission = UserFactory()

        cls.valid_data = {
            "name": "New Contract",
            "product": cls.product.pk,
            "start_date": "2024-01-01",
            "end_date": "2024-12-31",
            "cost": "2000.00",
        }

    def test_view_configuration(self) -> None:
        """Test view class configuration."""
        view = ContractsCreateView()

        self.assertEqual(view.permission_required, "contracts.add_contract")
        self.assertEqual(view.model, Contract)
        self.assertEqual(view.template_name, "contracts/contracts-create.html")
        self.assertEqual(view.form_class, ContractForm)
        self.assertEqual(view.success_url, reverse("contracts:list"))

    def test_view_requires_permission(self) -> None:
        """Test that view requires proper permission."""
        self.client.force_login(self.user_with_permission)
        response = self.client.get(reverse("contracts:create"))
        self.assertEqual(response.status_code, 200)

    def test_view_without_permission(self) -> None:
        """Test that view denies access without permission."""
        self.client.force_login(self.user_without_permission)
        response = self.client.get(reverse("contracts:create"))
        self.assertEqual(response.status_code, 403)

    def test_view_with_superuser(self) -> None:
        """Test that superuser can access the view."""
        self.client.force_login(self.superuser)
        response = self.client.get(reverse("contracts:create"))
        self.assertEqual(response.status_code, 200)

    def test_template_used(self) -> None:
        """Test that correct template is used."""
        self.client.force_login(self.user_with_permission)
        response = self.client.get(reverse("contracts:create"))
        self.assertTemplateUsed(response, "contracts/contracts-create.html")

    def test_context_contains_form(self) -> None:
        """Test that context contains form."""
        self.client.force_login(self.user_with_permission)
        response = self.client.get(reverse("contracts:create"))

        self.assertIn("form", response.context)
        self.assertIsInstance(response.context["form"], ContractForm)

    def test_successful_creation(self) -> None:
        """Test successful contract creation."""
        initial_count = Contract.objects.count()

        self.client.force_login(self.superuser)

        document_file = SimpleUploadedFile(
            "contract.pdf", b"file_content", content_type="application/pdf"
        )

        response = self.client.post(
            reverse("contracts:create"),
            data={**self.valid_data, "document": document_file},
        )

        self.assertEqual(response.status_code, 302)
        self.assertEqual(Contract.objects.count(), initial_count + 1)

        new_contract = Contract.objects.get(name="New Contract")
        self.assertEqual(new_contract.cost, 2000.00)
        self.assertEqual(new_contract.product, self.product)

    def test_redirect_after_creation(self) -> None:
        """Test redirect after successful creation."""
        self.client.force_login(self.superuser)

        document_file = SimpleUploadedFile(
            "contract.pdf", b"file_content", content_type="application/pdf"
        )

        response = self.client.post(
            reverse("contracts:create"),
            data={**self.valid_data, "document": document_file},
        )

        self.assertRedirects(response, reverse("contracts:list"))


class ContractDeleteViewTest(TestCase):
    """Tests for ContractDeleteView functionality.

    Attributes:
        contract (Contract): Contract instance for testing
        user_with_permission (User): User with delete_contract permission
        user_without_permission (User): User without delete_contract permission
        superuser (User): Superuser instance
    """

    @classmethod
    def setUpTestData(cls) -> None:
        """Create test data for all test methods."""
        cls.contract = ContractFactory()
        cls.superuser = UserFactory(is_superuser=True)

        cls.user_with_permission = UserFactory()
        delete_permission = Permission.objects.get(codename="delete_contract")
        cls.user_with_permission.user_permissions.add(delete_permission)

        cls.user_without_permission = UserFactory()

    def test_view_configuration(self) -> None:
        """Test view class configuration."""
        view = ContractDeleteView()

        self.assertEqual(view.permission_required, "contracts.delete_contract")
        self.assertEqual(view.model, Contract)
        self.assertEqual(view.template_name, "contracts/contracts-delete.html")
        self.assertEqual(view.success_url, reverse("contracts:list"))

    def test_view_requires_permission(self) -> None:
        """Test that view requires proper permission."""
        self.client.force_login(self.user_with_permission)
        response = self.client.get(
            reverse("contracts:delete", kwargs={"pk": self.contract.pk})
        )
        self.assertEqual(response.status_code, 200)

    def test_view_without_permission(self) -> None:
        """Test that view denies access without permission."""
        self.client.force_login(self.user_without_permission)
        response = self.client.get(
            reverse("contracts:delete", kwargs={"pk": self.contract.pk})
        )
        self.assertEqual(response.status_code, 403)

    def test_view_with_superuser(self) -> None:
        """Test that superuser can access the view."""
        self.client.force_login(self.superuser)
        response = self.client.get(
            reverse("contracts:delete", kwargs={"pk": self.contract.pk})
        )
        self.assertEqual(response.status_code, 200)

    def test_template_used(self) -> None:
        """Test that correct template is used."""
        self.client.force_login(self.user_with_permission)
        response = self.client.get(
            reverse("contracts:delete", kwargs={"pk": self.contract.pk})
        )
        self.assertTemplateUsed(response, "contracts/contracts-delete.html")

    def test_context_contains_contract(self) -> None:
        """Test that context contains the contract."""
        self.client.force_login(self.user_with_permission)
        response = self.client.get(
            reverse("contracts:delete", kwargs={"pk": self.contract.pk})
        )

        self.assertIn("object", response.context)
        self.assertEqual(response.context["object"], self.contract)

    def test_successful_deletion(self) -> None:
        """Test successful contract deletion."""
        contract_id = self.contract.pk

        self.client.force_login(self.user_with_permission)

        response = self.client.post(
            reverse("contracts:delete", kwargs={"pk": contract_id})
        )

        self.assertEqual(response.status_code, 302)
        self.assertFalse(Contract.objects.filter(pk=contract_id).exists())

    def test_redirect_after_deletion(self) -> None:
        """Test redirect after successful deletion."""
        self.client.force_login(self.superuser)

        response = self.client.post(
            reverse("contracts:delete", kwargs={"pk": self.contract.pk})
        )

        self.assertRedirects(response, reverse("contracts:list"))
