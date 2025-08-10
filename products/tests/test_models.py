from django.core.exceptions import ValidationError
from django.test import TestCase
from django.utils.translation import gettext as _

from products.models import Product
from products.tests.conftest import ProductFactory


class ProductModelTest(TestCase):
    """Тесты для модели Product."""

    @classmethod
    def setUpTestData(cls):
        """Создание тестовых данных один раз для всех тестов."""
        cls.product = ProductFactory()
        cls.long_description = (
            "Lorem ipsum dolor sit amet, consectetur adipiscing elit. " * 3
        )
        cls.short_description = "Short description"

    def test_string_representation(self):
        """Тест строкового представления модели."""
        self.assertEqual(
            str(self.product),
            f"Product(pk={self.product.pk}, name={self.product.name})",
        )

    def test_short_description_with_none(self):
        """Тест short_description при отсутствии описания."""
        product = ProductFactory(description=None)
        self.assertEqual(product.short_description, _("No description"))

    def test_short_description_with_short_text(self):
        """Тест short_description с текстом короче 50 символов."""
        product = ProductFactory(description=self.short_description)
        self.assertEqual(product.short_description, self.short_description)

    def test_short_description_with_long_text(self):
        """Тест short_description с текстом длиннее 50 символов."""
        product = ProductFactory(description=self.long_description)
        expected = self.long_description[:50] + "..."
        self.assertEqual(product.short_description, expected)
        self.assertEqual(len(product.short_description), 53)

    def test_short_description_edge_cases(self):
        """Тест граничных случаев для short_description."""
        # Точная граница (50 символов)
        exact_length = "a" * 50
        product = ProductFactory(description=exact_length)
        self.assertEqual(product.short_description, exact_length)

        # Граница + 1 символ
        over_length = "b" * 51
        product = ProductFactory(description=over_length)
        self.assertEqual(product.short_description, "b" * 50 + "...")

    def test_model_meta_options(self):
        """Тест мета-опций модели."""
        meta = Product._meta
        self.assertEqual(meta.verbose_name, _("Product"))
        self.assertEqual(meta.verbose_name_plural, _("Products"))
        self.assertEqual(meta.ordering, ["name"])

    def test_get_absolute_url(self):
        """Тест метода get_absolute_url."""
        url = self.product.get_absolute_url()
        self.assertEqual(url, f"/products/{self.product.pk}/")

    def test_cost_validation(self):
        """Тест валидации стоимости."""
        product = ProductFactory.build(cost=-100)
        with self.assertRaises(ValidationError):
            product.full_clean()
