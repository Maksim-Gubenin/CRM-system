from factory import Faker
from factory.django import DjangoModelFactory

from products.models import Product


class ProductFactory(DjangoModelFactory):
    """Фабрика для создания тестовых продуктов."""

    class Meta:
        model = Product
        django_get_or_create = ("name",)  # Оптимизация для избежания дублирования

    name = Faker("word")
    description = Faker("text", max_nb_chars=300)  # Контролируемая длина
    cost = Faker("pydecimal", left_digits=3, right_digits=2, positive=True)
    is_active = True
