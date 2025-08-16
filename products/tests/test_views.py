from decimal import Decimal
from typing import Any, Dict

from django.contrib.auth import get_user_model
from django.test import TestCase, override_settings
from django.urls import reverse

from crm.utils import ProductFactory, UserFactory
from products.models import Product
from products.views import ProductsUpdateView

User = get_user_model()


class ProductsListViewTest(TestCase):
    """Tests for ProductsListView functionality.

    Attributes:
        product_active (Product): Active product instance
        product_not_active (Product): Inactive product instance
        superuser (User): Superuser instance
        user (User): Regular user instance
    """

    @classmethod
    def setUpTestData(cls) -> None:
        """Create test data for all test methods."""
        cls.product_active = ProductFactory()
        cls.product_not_active = ProductFactory(is_active=False)
        cls.superuser = UserFactory(is_superuser=True)
        cls.user = UserFactory(is_superuser=False)

    def test_view_url_exists(self) -> None:
        """Test that view URL is accessible."""
        response = self.client.get(reverse("products:list"))
        self.assertEqual(response.status_code, 302)

    def test_view_with_permission(self) -> None:
        """Test view access with proper permissions."""
        self.client.force_login(self.superuser)
        response = self.client.get(reverse("products:list"))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "products/products-list.html")

    def test_view_without_permission(self) -> None:
        """Test view access without permissions."""
        self.client.force_login(self.user)
        response = self.client.get(reverse("products:list"))
        self.assertEqual(response.status_code, 403)

    def test_only_active_products(self) -> None:
        """Test that only active products are displayed."""
        self.client.force_login(self.superuser)
        response = self.client.get(reverse("products:list"))
        self.assertEqual(len(response.context["products"]), 1)
        self.assertIn(self.product_active, response.context["products"])
        self.assertNotIn(self.product_not_active, response.context["products"])


class ProductsDetailViewTest(TestCase):
    """Tests for ProductsDetailView functionality."""

    @classmethod
    def setUpTestData(cls) -> None:
        """Create test data for all test methods."""
        cls.product_active = ProductFactory()
        cls.product_not_active = ProductFactory(is_active=False)
        cls.superuser = UserFactory(is_superuser=True)
        cls.user = UserFactory(is_superuser=False)

    def test_view_url_exists(self) -> None:
        """Test that view URL is accessible."""
        response = self.client.get(
            reverse("products:detail", kwargs={"pk": self.product_active.pk})
        )
        self.assertEqual(response.status_code, 302)

    def test_view_with_permission(self) -> None:
        """Test view access with proper permissions."""
        self.client.force_login(self.superuser)
        response = self.client.get(
            reverse("products:detail", kwargs={"pk": self.product_active.pk})
        )
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "products/products-detail.html")

    def test_view_without_permission(self) -> None:
        """Test view access without permissions."""
        self.client.force_login(self.user)
        response = self.client.get(
            reverse("products:detail", kwargs={"pk": self.product_active.pk})
        )
        self.assertEqual(response.status_code, 403)

    def test_only_active_products(self) -> None:
        """Test that only active products can be viewed."""
        self.client.force_login(self.superuser)
        response_active = self.client.get(
            reverse("products:detail", kwargs={"pk": self.product_active.pk})
        )
        response_inactive = self.client.get(
            reverse("products:detail", kwargs={"pk": self.product_not_active.pk})
        )
        self.assertEqual(response_active.status_code, 200)
        self.assertEqual(response_inactive.status_code, 404)


class ProductsUpdateViewTest(TestCase):
    """Tests for ProductsUpdateView functionality."""

    @classmethod
    def setUpTestData(cls) -> None:
        """Create test data for all test methods."""
        cls.product_active = ProductFactory()
        cls.product_not_active = ProductFactory(is_active=False)
        cls.superuser = UserFactory(is_superuser=True)
        cls.user = UserFactory(is_superuser=False)
        cls.valid_data: Dict[str, Any] = {
            "name": "Updated name",
            "description": "Updated description",
            "cost": Decimal("999.99"),
        }
        cls.invalid_data: Dict[str, Any] = {
            "name": "",
            "description": "Test",
            "cost": -100,
        }

    def test_view_url_exists(self) -> None:
        """Test that view URL is accessible."""
        response = self.client.get(
            reverse("products:update", kwargs={"pk": self.product_active.pk})
        )
        self.assertEqual(response.status_code, 302)

    def test_view_with_permission(self) -> None:
        """Test view access with proper permissions."""
        self.client.force_login(self.superuser)
        response = self.client.get(
            reverse("products:update", kwargs={"pk": self.product_active.pk})
        )
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "products/products-update.html")

    def test_view_without_permission(self) -> None:
        """Test view access without permissions."""
        self.client.force_login(self.user)
        response = self.client.get(
            reverse("products:update", kwargs={"pk": self.product_active.pk})
        )
        self.assertEqual(response.status_code, 403)

    def test_only_active_products(self) -> None:
        """Test that only active products can be updated."""
        self.client.force_login(self.superuser)
        response_active = self.client.get(
            reverse("products:update", kwargs={"pk": self.product_active.pk})
        )
        response_inactive = self.client.get(
            reverse("products:update", kwargs={"pk": self.product_not_active.pk})
        )
        self.assertEqual(response_active.status_code, 200)
        self.assertEqual(response_inactive.status_code, 404)

    def test_update_products_valid(self) -> None:
        """Test successful product update with valid data."""
        self.client.force_login(self.superuser)
        response = self.client.post(
            reverse("products:update", kwargs={"pk": self.product_active.pk}),
            data=self.valid_data,
        )
        updated_product = Product.objects.get(pk=self.product_active.pk)
        self.assertEqual(response.status_code, 302)  # Should redirect on success
        self.assertEqual(updated_product.name, self.valid_data["name"])
        self.assertEqual(updated_product.description, self.valid_data["description"])
        self.assertEqual(updated_product.cost, self.valid_data["cost"])

    def test_update_products_invalid(self) -> None:
        """Test product update with invalid data."""
        self.client.force_login(self.superuser)
        response = self.client.post(
            reverse("products:update", kwargs={"pk": self.product_active.pk}),
            data=self.invalid_data,
        )
        product = Product.objects.get(pk=self.product_active.pk)
        self.assertEqual(response.status_code, 200)  # Should stay on form page
        form = response.context["form"]
        self.assertFalse(form.is_valid())
        self.assertIn("name", form.errors)
        self.assertIn("cost", form.errors)
        self.assertNotEqual(product.name, self.invalid_data["name"])
        self.assertNotEqual(product.cost, self.invalid_data["cost"])

    def test_get_success_url_coverage(self):
        """Test specifically for coverage of get_success_url method."""
        self.client.force_login(self.superuser)
        view = ProductsUpdateView()

        view.object = self.product_active

        result = view.get_success_url()

        self.assertEqual(result, self.product_active.get_absolute_url())

    def test_update_view_redirect_flow(self):
        """Test full update flow including success_url."""
        self.client.force_login(self.superuser)

        response = self.client.post(
            reverse("products:update", kwargs={"pk": self.product_active.pk}),
            data=self.valid_data,
        )

        self.assertRedirects(
            response,
            reverse("products:detail", kwargs={"pk": self.product_active.pk}),
            status_code=302,
            target_status_code=200,
        )


@override_settings(USE_I18N=False)
class ProductsDeleteViewTest(TestCase):
    """Tests for ProductsDeleteView functionality."""

    @classmethod
    def setUpTestData(cls) -> None:
        """Create test data for all test methods."""
        cls.product_active = ProductFactory()
        cls.product_not_active = ProductFactory(is_active=False)
        cls.superuser = UserFactory(is_superuser=True)
        cls.user = UserFactory(is_superuser=False)

    def test_view_url_exists(self) -> None:
        """Test that view URL is accessible."""
        response = self.client.get(
            reverse("products:delete", kwargs={"pk": self.product_active.pk})
        )
        self.assertEqual(response.status_code, 302)

    def test_view_with_permission(self) -> None:
        """Test view access with proper permissions."""
        self.client.force_login(self.superuser)
        response = self.client.post(
            reverse("products:delete", kwargs={"pk": self.product_active.pk})
        )
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, reverse("products:list"))

    def test_view_without_permission(self) -> None:
        """Test view access without permissions."""
        self.client.force_login(self.user)
        response = self.client.post(
            reverse("products:delete", kwargs={"pk": self.product_active.pk})
        )
        self.assertEqual(response.status_code, 403)

    def test_only_active_products(self) -> None:
        """Test that only active products can be deleted."""
        self.client.force_login(self.superuser)
        response_active = self.client.post(
            reverse("products:delete", kwargs={"pk": self.product_active.pk})
        )
        response_inactive = self.client.post(
            reverse("products:delete", kwargs={"pk": self.product_not_active.pk})
        )
        self.assertEqual(response_active.status_code, 302)
        self.assertEqual(response_inactive.status_code, 404)

    def test_delete_products(self) -> None:
        """Test successful product deletion."""
        self.client.force_login(self.superuser)

        # Проверяем, что продукт существует до удаления
        self.assertTrue(Product.objects.filter(pk=self.product_active.pk).exists())

        response = self.client.post(
            reverse("products:delete", kwargs={"pk": self.product_active.pk})
        )

        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, reverse("products:list"))
        self.assertFalse(Product.objects.filter(pk=self.product_active.pk).exists())
