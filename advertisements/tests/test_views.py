from django.core.cache import cache
from django.test import TestCase
from django.urls import reverse

from advertisements.models import Advertisement
from advertisements.views import ADSUpdateView
from crm.utils.factories import AdvertisementFactory, ProductFactory, UserFactory


class ADSListViewTest(TestCase):
    """Tests for ADSListView functionality.

    Attributes:
        active_ads (List[Advertisement]): List of active advertisement instances
        inactive_ads (List[Advertisement]): List of inactive advertisement instances
        superuser (User): Superuser instance
    """

    def setUp(self):
        """Set up test environment.

        Clears cache before each test to prevent interference from
        cached data between test runs.
        """
        cache.clear()

    @classmethod
    def setUpTestData(cls) -> None:
        """Create test data for all test methods."""
        cls.active_ads = AdvertisementFactory.create_batch(3, is_active=True)
        cls.inactive_ads = AdvertisementFactory.create_batch(2, is_active=False)
        cls.superuser = UserFactory(is_superuser=True)

    def test_view_requires_login(self) -> None:
        """Test that dashboard view requires authentication."""
        response = self.client.get(reverse("advertisements:list"))
        self.assertEqual(response.status_code, 302)
        self.assertIn("/login/", response.url)

    def test_view_with_superuser(self) -> None:
        """Test that superuser can access the view."""
        self.client.force_login(self.superuser)
        response = self.client.get(reverse("advertisements:list"))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "advertisements/ads-list.html")

    def test_only_active_advertisements(self) -> None:
        """Test that only active advertisements are displayed."""
        self.client.force_login(self.superuser)
        response = self.client.get(reverse("advertisements:list"))

        ads_in_context = response.context["ads"]
        self.assertEqual(len(ads_in_context), 3)

        for ad in self.active_ads:
            self.assertIn(ad, ads_in_context)

        for ad in self.inactive_ads:
            self.assertNotIn(ad, ads_in_context)

    def test_pagination(self) -> None:
        """Test that pagination works correctly."""
        AdvertisementFactory.create_batch(25, is_active=True)

        self.client.force_login(self.superuser)
        response = self.client.get(reverse("advertisements:list"))

        self.assertTrue(response.context["is_paginated"])
        self.assertEqual(len(response.context["ads"]), 20)

    def test_context_object_name(self) -> None:
        """Test that context object name is correct."""
        self.client.force_login(self.superuser)
        response = self.client.get(reverse("advertisements:list"))
        self.assertIn("ads", response.context)


class ADSDetailViewTest(TestCase):
    """Tests for ADSDetailView functionality.

    Attributes:
        active_ad (Advertisement): Active advertisement instance
        inactive_ad (Advertisement): Inactive advertisement instance
        superuser (User): Superuser instance
    """

    def setUp(self):
        """Set up test environment.

        Clears cache before each test to prevent interference from
        cached data between test runs.
        """
        cache.clear()

    @classmethod
    def setUpTestData(cls) -> None:
        """Create test data for all test methods."""
        cls.active_ad = AdvertisementFactory(is_active=True)
        cls.inactive_ad = AdvertisementFactory(is_active=False)
        cls.superuser = UserFactory(is_superuser=True)

    def test_view_active_advertisement(self) -> None:
        """Test that active advertisement can be viewed."""
        self.client.force_login(self.superuser)
        response = self.client.get(
            reverse("advertisements:detail", kwargs={"pk": self.active_ad.pk})
        )
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "advertisements/ads-detail.html")

    def test_view_inactive_advertisement(self) -> None:
        """Test that inactive advertisement returns 404."""
        self.client.force_login(self.superuser)
        response = self.client.get(
            reverse("advertisements:detail", kwargs={"pk": self.inactive_ad.pk})
        )
        self.assertEqual(response.status_code, 404)

    def test_context_contains_advertisement(self) -> None:
        """Test that context contains the advertisement."""
        self.client.force_login(self.superuser)
        response = self.client.get(
            reverse("advertisements:detail", kwargs={"pk": self.active_ad.pk})
        )
        self.assertEqual(response.context["object"], self.active_ad)
        self.assertEqual(response.context["advertisement"], self.active_ad)


class ADSUpdateViewTest(TestCase):
    """Tests for ADSUpdateView functionality.

    Attributes:
        active_ad (Advertisement): Active advertisement instance
        inactive_ad (Advertisement): Inactive advertisement instance
        superuser (User): Superuser instance
        valid_data (Dict): Valid test data for update
    """

    @classmethod
    def setUpTestData(cls) -> None:
        """Create test data for all test methods."""
        cls.active_ad = AdvertisementFactory(is_active=True)
        cls.inactive_ad = AdvertisementFactory(is_active=False)
        cls.superuser = UserFactory(is_superuser=True)

        cls.valid_data = {
            "name": "Updated Campaign",
            "channel": "social",
            "cost": 1500.00,
            "product": cls.active_ad.product.pk,
        }

    def test_view_active_advertisement(self) -> None:
        """Test that active advertisement can be updated."""
        self.client.force_login(self.superuser)
        response = self.client.get(
            reverse("advertisements:update", kwargs={"pk": self.active_ad.pk})
        )
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "advertisements/ads-update.html")

    def test_view_inactive_advertisement(self) -> None:
        """Test that inactive advertisement returns 404."""
        self.client.force_login(self.superuser)
        response = self.client.get(
            reverse("advertisements:update", kwargs={"pk": self.inactive_ad.pk})
        )
        self.assertEqual(response.status_code, 404)

    def test_update_advertisement_valid_data(self) -> None:
        """Test successful advertisement update with valid data."""
        self.client.force_login(self.superuser)
        response = self.client.post(
            reverse("advertisements:update", kwargs={"pk": self.active_ad.pk}),
            data=self.valid_data,
        )

        self.assertEqual(response.status_code, 302)

        updated_ad = Advertisement.objects.get(pk=self.active_ad.pk)
        self.assertEqual(updated_ad.name, "Updated Campaign")
        self.assertEqual(updated_ad.cost, 1500.00)

    def test_get_success_url(self) -> None:
        """Test that success URL redirects to detail view."""
        self.client.force_login(self.superuser)
        view = ADSUpdateView()
        view.object = self.active_ad

        success_url = view.get_success_url()
        self.assertEqual(success_url, self.active_ad.get_absolute_url())


class ADSCreateViewTest(TestCase):
    """Tests for ADSCreateView functionality.

    Attributes:
        product (Product): Product instance for testing
        superuser (User): Superuser instance
        valid_data (Dict): Valid test data for creation
    """

    @classmethod
    def setUpTestData(cls) -> None:
        """Create test data for all test methods."""
        cls.product = ProductFactory()
        cls.superuser = UserFactory(is_superuser=True)

        cls.valid_data = {
            "name": "New Campaign",
            "channel": "email",
            "cost": 2000.00,
            "product": cls.product.pk,
        }

    def test_view_accessible_with_superuser(self) -> None:
        """Test that view is accessible with superuser."""
        self.client.force_login(self.superuser)
        response = self.client.get(reverse("advertisements:create"))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "advertisements/ads-create.html")

    def test_create_advertisement_valid_data(self) -> None:
        """Test successful advertisement creation with valid data."""
        initial_count = Advertisement.objects.count()

        self.client.force_login(self.superuser)

        self.client.get(reverse("advertisements:create"))

        url = reverse("advertisements:create")

        response = self.client.post(url, data=self.valid_data)

        self.assertEqual(response.status_code, 302)
        self.assertEqual(Advertisement.objects.count(), initial_count + 1)

    def test_success_url_redirect(self) -> None:
        """Test that success URL redirects to list view."""
        self.client.force_login(self.superuser)
        response = self.client.post(
            reverse("advertisements:create"), data=self.valid_data
        )

        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, reverse("advertisements:list"))


class ADSDeleteViewTest(TestCase):
    """Tests for ADSDeleteView functionality.

    Attributes:
        active_ad (Advertisement): Active advertisement instance
        inactive_ad (Advertisement): Inactive advertisement instance
        superuser (User): Superuser instance
    """

    @classmethod
    def setUpTestData(cls) -> None:
        """Create test data for all test methods."""
        cls.active_ad = AdvertisementFactory(is_active=True)
        cls.inactive_ad = AdvertisementFactory(is_active=False)
        cls.superuser = UserFactory(is_superuser=True)

    def test_view_active_advertisement(self) -> None:
        """Test that active advertisement can be deleted."""
        self.client.force_login(self.superuser)
        response = self.client.get(
            reverse("advertisements:delete", kwargs={"pk": self.active_ad.pk})
        )
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "advertisements/ads-delete.html")

    def test_view_inactive_advertisement(self) -> None:
        """Test that inactive advertisement returns 404."""
        self.client.force_login(self.superuser)
        response = self.client.get(
            reverse("advertisements:delete", kwargs={"pk": self.inactive_ad.pk})
        )
        self.assertEqual(response.status_code, 404)

    def test_delete_advertisement(self) -> None:
        """Test successful advertisement deletion."""
        self.client.force_login(self.superuser)

        self.assertTrue(Advertisement.objects.filter(pk=self.active_ad.pk).exists())

        response = self.client.post(
            reverse("advertisements:delete", kwargs={"pk": self.active_ad.pk})
        )

        self.assertEqual(response.status_code, 302)
        self.assertFalse(Advertisement.objects.filter(pk=self.active_ad.pk).exists())

    def test_success_url_redirect(self) -> None:
        """Test that success URL redirects to list view."""
        self.client.force_login(self.superuser)
        response = self.client.post(
            reverse("advertisements:delete", kwargs={"pk": self.active_ad.pk})
        )

        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, reverse("advertisements:list"))


class ADSStatisticsViewTest(TestCase):
    """Tests for ADSStatisticsView functionality.

    Attributes:
        ads (List[Advertisement]): List of advertisement instances
        superuser (User): Superuser instance
    """

    @classmethod
    def setUpTestData(cls) -> None:
        """Create test data for all test methods."""
        cls.ads = AdvertisementFactory.create_batch(3)
        cls.superuser = UserFactory(is_superuser=True)

    def test_view_accessible_with_superuser(self) -> None:
        """Test that view is accessible with superuser."""
        self.client.force_login(self.superuser)
        response = self.client.get(reverse("advertisements:statistic"))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "advertisements/ads-statistic.html")

    def test_context_contains_all_advertisements(self) -> None:
        """Test that context contains all advertisements (including inactive)."""
        inactive_ad = AdvertisementFactory(is_active=False)

        self.client.force_login(self.superuser)
        response = self.client.get(reverse("advertisements:statistic"))

        ads_in_context = response.context["ads"]
        self.assertEqual(ads_in_context.count(), 4)

        self.assertIn(inactive_ad, ads_in_context)

    def test_context_structure(self) -> None:
        """Test that context has correct structure."""
        self.client.force_login(self.superuser)
        response = self.client.get(reverse("advertisements:statistic"))

        self.assertIn("ads", response.context)
        self.assertIsInstance(response.context["ads"].first(), Advertisement)
