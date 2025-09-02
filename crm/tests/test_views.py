from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse

from advertisements.models import Advertisement
from crm.utils.factories import (
    AdvertisementFactory,
    CustomerFactory,
    LeadFactory,
    ProductFactory,
)
from customers.models import Customer
from leads.models import Lead
from products.models import Product

User = get_user_model()


class DashboardViewTest(TestCase):
    """Tests for dashboard_view functionality."""

    @classmethod
    def setUpTestData(cls) -> None:
        """Set up test data for all test methods."""
        cls.user = User.objects.create_user(username="testuser", password="testpass123")
        cls.url = reverse("crm:dashboard")

    def test_dashboard_requires_login(self) -> None:
        """Test that dashboard view requires authentication."""
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 302)
        self.assertTrue(response.url.startswith("/accounts/login/"))

    def test_dashboard_accessible_to_authenticated_user(self) -> None:
        """Test that authenticated user can access dashboard."""
        self.client.login(username="testuser", password="testpass123")
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "index.html")

    def test_dashboard_context_with_no_data(self) -> None:
        """Test dashboard context when no data exists."""
        self.client.login(username="testuser", password="testpass123")
        response = self.client.get(self.url)

        context = response.context
        self.assertEqual(context["products_count"], 0)
        self.assertEqual(context["advertisements_count"], 0)
        self.assertEqual(context["leads_count"], 0)
        self.assertEqual(context["customers_count"], 0)

    def test_dashboard_context_with_multiple_records(self) -> None:
        """Test dashboard context with multiple records of each type."""
        ProductFactory.create_batch(3)
        AdvertisementFactory.create_batch(5)
        LeadFactory.create_batch(2)
        CustomerFactory.create_batch(4)

        self.client.login(username="testuser", password="testpass123")
        response = self.client.get(self.url)

        context = response.context
        self.assertEqual(context["products_count"], Product.objects.count())
        self.assertEqual(context["advertisements_count"], Advertisement.objects.count())
        self.assertEqual(context["leads_count"], Lead.objects.count())
        self.assertEqual(context["customers_count"], Customer.objects.count())

    def test_dashboard_template_content(self) -> None:
        """Test that dashboard template receives correct context variables."""
        ProductFactory.create_batch(2)
        AdvertisementFactory.create_batch(3)

        self.client.login(username="testuser", password="testpass123")
        response = self.client.get(self.url)

        self.assertIn("products_count", response.context)
        self.assertIn("advertisements_count", response.context)
        self.assertIn("leads_count", response.context)
        self.assertIn("customers_count", response.context)

    def test_dashboard_view_uses_correct_template(self) -> None:
        """Test that dashboard view uses the correct template."""
        self.client.login(username="testuser", password="testpass123")
        response = self.client.get(self.url)
        self.assertTemplateUsed(response, "index.html")
