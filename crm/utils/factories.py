from django.contrib.auth import get_user_model
from factory import Faker
from factory.django import DjangoModelFactory

from products.models import Product

User = get_user_model()


class ProductFactory(DjangoModelFactory):
    """
    Creates Product instances with realistic test data.
    Automatically generates: name, description, cost and active status.
    """

    class Meta:
        """Meta class configuration"""

        model = Product
        django_get_or_create = ("name",)

    name = Faker("word")
    description = Faker("text", max_nb_chars=300)
    cost = Faker("pydecimal", left_digits=3, right_digits=2, positive=True)
    is_active = True


class UserFactory(DjangoModelFactory):
    """
    Creates Django User instances for testing.
    Generates random usernames and passwords.
    """

    class Meta:
        """Meta class configuration"""

        model = User

    username = Faker("name")
    password = Faker("password")
