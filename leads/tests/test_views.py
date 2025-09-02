from django.contrib.auth.models import Permission
from django.contrib.contenttypes.models import ContentType
from django.test import TestCase
from django.urls import reverse

from crm.utils.factories import AdvertisementFactory, UserFactory
from leads.models import Lead
from leads.views import LeadsUpdateView


class LeadsListViewTest(TestCase):
    """Tests for LeadsListView functionality."""

    @classmethod
    def setUpTestData(cls) -> None:
        """Create test data for all test methods."""
        cls.leads = Lead.objects.bulk_create(
            [
                Lead(
                    first_name="John",
                    last_name="Doe",
                    phone="+1234567890",
                    email="john@example.com",
                    advertisement=AdvertisementFactory(),
                ),
                Lead(
                    first_name="Jane",
                    last_name="Smith",
                    phone="+0987654321",
                    email="jane@example.com",
                    advertisement=AdvertisementFactory(),
                ),
            ]
        )

        cls.user = UserFactory()
        content_type = ContentType.objects.get_for_model(Lead)
        permission = Permission.objects.get(
            codename="view_lead", content_type=content_type
        )
        cls.user.user_permissions.add(permission)

    def test_view_requires_permission(self) -> None:
        """Test that view requires proper permission."""
        unauthorized_user = UserFactory()
        self.client.force_login(unauthorized_user)

        response = self.client.get(reverse("leads:list"))
        self.assertEqual(response.status_code, 403)

    def test_view_with_permission(self) -> None:
        """Test that user with permission can access the view."""
        self.client.force_login(self.user)
        response = self.client.get(reverse("leads:list"))

        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "leads/leads-list.html")

    def test_context_contains_leads(self) -> None:
        """Test that context contains all leads."""
        self.client.force_login(self.user)
        response = self.client.get(reverse("leads:list"))

        leads_in_context = list(response.context["leads"])
        self.assertEqual(len(leads_in_context), 2)
        self.assertCountEqual(leads_in_context, self.leads)

    def test_ordering_by_created_at_desc(self) -> None:
        """Test that leads are ordered by created_at descending."""
        self.client.force_login(self.user)
        response = self.client.get(reverse("leads:list"))

        leads = list(response.context["leads"])
        self.assertEqual(leads[0], self.leads[1])
        self.assertEqual(leads[1], self.leads[0])

    def test_pagination(self) -> None:
        """Test that pagination works correctly."""
        extra_leads = []
        for i in range(25):
            extra_leads.append(
                Lead(
                    first_name=f"Extra{i}",
                    last_name="Lead",
                    phone=f"+111111111{i}",
                    email=f"extra{i}@example.com",
                    advertisement=AdvertisementFactory(),
                )
            )
        Lead.objects.bulk_create(extra_leads)

        self.client.force_login(self.user)
        response = self.client.get(reverse("leads:list"))

        self.assertTrue(response.context["is_paginated"])
        self.assertEqual(len(response.context["leads"]), 20)

    def test_context_object_name(self) -> None:
        """Test that context object name is correct."""
        self.client.force_login(self.user)
        response = self.client.get(reverse("leads:list"))
        self.assertIn("leads", response.context)


class LeadsDetailViewTest(TestCase):
    """Tests for LeadsDetailView functionality."""

    @classmethod
    def setUpTestData(cls) -> None:
        """Create test data for all test methods."""
        cls.lead = Lead.objects.create(
            first_name="John",
            last_name="Doe",
            phone="+1234567890",
            email="john@example.com",
            advertisement=AdvertisementFactory(),
        )

        cls.user = UserFactory()
        content_type = ContentType.objects.get_for_model(Lead)
        permission = Permission.objects.get(
            codename="view_lead", content_type=content_type
        )
        cls.user.user_permissions.add(permission)

    def test_view_requires_permission(self) -> None:
        """Test that view requires proper permission."""
        unauthorized_user = UserFactory()
        self.client.force_login(unauthorized_user)

        response = self.client.get(reverse("leads:detail", kwargs={"pk": self.lead.pk}))
        self.assertEqual(response.status_code, 403)

    def test_view_with_permission(self) -> None:
        """Test that user with permission can access the view."""
        self.client.force_login(self.user)
        response = self.client.get(reverse("leads:detail", kwargs={"pk": self.lead.pk}))

        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "leads/leads-detail.html")

    def test_context_contains_lead(self) -> None:
        """Test that context contains the correct lead."""
        self.client.force_login(self.user)
        response = self.client.get(reverse("leads:detail", kwargs={"pk": self.lead.pk}))

        self.assertEqual(response.context["object"], self.lead)
        self.assertEqual(response.context["lead"], self.lead)

    def test_nonexistent_lead_returns_404(self) -> None:
        """Test that non-existent lead returns 404."""
        self.client.force_login(self.user)
        response = self.client.get(reverse("leads:detail", kwargs={"pk": 999}))
        self.assertEqual(response.status_code, 404)


class LeadsUpdateViewTest(TestCase):
    """Tests for LeadsUpdateView functionality."""

    @classmethod
    def setUpTestData(cls) -> None:
        """Create test data for all test methods."""
        cls.lead = Lead.objects.create(
            first_name="John",
            last_name="Doe",
            phone="+1234567890",
            email="john@example.com",
            advertisement=AdvertisementFactory(),
        )

        cls.other_advertisement = AdvertisementFactory()

        cls.user = UserFactory()
        content_type = ContentType.objects.get_for_model(Lead)
        permission = Permission.objects.get(
            codename="change_lead", content_type=content_type
        )
        cls.user.user_permissions.add(permission)

        cls.valid_data = {
            "first_name": "Updated",
            "last_name": "Name",
            "phone": "+9999999999",
            "email": "updated@example.com",
            "advertisement": cls.other_advertisement.pk,
        }

    def test_view_requires_permission(self) -> None:
        """Test that view requires proper permission."""
        unauthorized_user = UserFactory()
        self.client.force_login(unauthorized_user)

        response = self.client.get(reverse("leads:update", kwargs={"pk": self.lead.pk}))
        self.assertEqual(response.status_code, 403)

    def test_view_with_permission(self) -> None:
        """Test that user with permission can access the view."""
        self.client.force_login(self.user)
        response = self.client.get(reverse("leads:update", kwargs={"pk": self.lead.pk}))

        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "leads/leads-update.html")

    def test_update_lead_valid_data(self) -> None:
        """Test successful lead update with valid data."""
        self.client.force_login(self.user)
        response = self.client.post(
            reverse("leads:update", kwargs={"pk": self.lead.pk}), data=self.valid_data
        )

        self.assertEqual(response.status_code, 302)

        updated_lead = Lead.objects.get(pk=self.lead.pk)
        self.assertEqual(updated_lead.first_name, "Updated")
        self.assertEqual(updated_lead.last_name, "Name")
        self.assertEqual(updated_lead.phone, "+9999999999")
        self.assertEqual(updated_lead.email, "updated@example.com")
        self.assertEqual(updated_lead.advertisement, self.other_advertisement)

    def test_get_success_url(self) -> None:
        """Test that success URL redirects to detail view."""
        self.client.force_login(self.user)
        view = LeadsUpdateView()
        view.object = self.lead

        success_url = view.get_success_url()
        self.assertEqual(success_url, self.lead.get_absolute_url())

    def test_nonexistent_lead_returns_404(self) -> None:
        """Test that non-existent lead returns 404."""
        self.client.force_login(self.user)
        response = self.client.get(reverse("leads:update", kwargs={"pk": 999}))
        self.assertEqual(response.status_code, 404)


class LeadsCreateViewTest(TestCase):
    """Tests for LeadsCreateView functionality."""

    @classmethod
    def setUpTestData(cls) -> None:
        """Create test data for all test methods."""
        cls.advertisement = AdvertisementFactory()

        cls.user = UserFactory()
        content_type = ContentType.objects.get_for_model(Lead)
        permission = Permission.objects.get(
            codename="add_lead", content_type=content_type
        )
        cls.user.user_permissions.add(permission)

        cls.valid_data = {
            "first_name": "New",
            "last_name": "Lead",
            "phone": "+1234567890",
            "email": "new@example.com",
            "advertisement": cls.advertisement.pk,
        }

    def test_view_requires_permission(self) -> None:
        """Test that view requires proper permission."""
        unauthorized_user = UserFactory()
        self.client.force_login(unauthorized_user)

        response = self.client.get(reverse("leads:create"))
        self.assertEqual(response.status_code, 403)

    def test_view_with_permission(self) -> None:
        """Test that user with permission can access the view."""
        self.client.force_login(self.user)
        response = self.client.get(reverse("leads:create"))

        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "leads/leads-create.html")

    def test_create_lead_valid_data(self) -> None:
        """Test successful lead creation with valid data."""
        initial_count = Lead.objects.count()

        self.client.force_login(self.user)
        response = self.client.post(reverse("leads:create"), data=self.valid_data)

        self.assertEqual(response.status_code, 302)
        self.assertEqual(Lead.objects.count(), initial_count + 1)

        new_lead = Lead.objects.latest("created_at")
        self.assertEqual(new_lead.first_name, "New")
        self.assertEqual(new_lead.last_name, "Lead")
        self.assertEqual(new_lead.phone, "+1234567890")
        self.assertEqual(new_lead.email, "new@example.com")
        self.assertEqual(new_lead.advertisement, self.advertisement)

    def test_success_url_redirect(self) -> None:
        """Test that success URL redirects to list view."""
        self.client.force_login(self.user)
        response = self.client.post(reverse("leads:create"), data=self.valid_data)

        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, reverse("leads:list"))


class LeadsDeleteViewTest(TestCase):
    """Tests for LeadsDeleteView functionality."""

    @classmethod
    def setUpTestData(cls) -> None:
        """Create test data for all test methods."""
        cls.lead = Lead.objects.create(
            first_name="John",
            last_name="Doe",
            phone="+1234567890",
            email="john@example.com",
            advertisement=AdvertisementFactory(),
        )

        cls.user = UserFactory()
        content_type = ContentType.objects.get_for_model(Lead)
        permission = Permission.objects.get(
            codename="delete_lead", content_type=content_type
        )
        cls.user.user_permissions.add(permission)

    def test_view_requires_permission(self) -> None:
        """Test that view requires proper permission."""
        unauthorized_user = UserFactory()
        self.client.force_login(unauthorized_user)

        response = self.client.get(reverse("leads:delete", kwargs={"pk": self.lead.pk}))
        self.assertEqual(response.status_code, 403)

    def test_view_with_permission(self) -> None:
        """Test that user with permission can access the view."""
        self.client.force_login(self.user)
        response = self.client.get(reverse("leads:delete", kwargs={"pk": self.lead.pk}))

        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "leads/leads-delete.html")

    def test_delete_lead(self) -> None:
        """Test successful lead deletion."""
        self.client.force_login(self.user)

        self.assertTrue(Lead.objects.filter(pk=self.lead.pk).exists())

        response = self.client.post(
            reverse("leads:delete", kwargs={"pk": self.lead.pk})
        )

        self.assertEqual(response.status_code, 302)
        self.assertFalse(Lead.objects.filter(pk=self.lead.pk).exists())

    def test_success_url_redirect(self) -> None:
        """Test that success URL redirects to list view."""
        self.client.force_login(self.user)
        response = self.client.post(
            reverse("leads:delete", kwargs={"pk": self.lead.pk})
        )

        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, reverse("leads:list"))

    def test_nonexistent_lead_returns_404(self) -> None:
        """Test that non-existent lead returns 404."""
        self.client.force_login(self.user)
        response = self.client.get(reverse("leads:delete", kwargs={"pk": 999}))
        self.assertEqual(response.status_code, 404)
