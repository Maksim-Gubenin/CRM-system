from django.contrib.auth import get_user_model
from django.core.files.uploadedfile import SimpleUploadedFile
from factory import Faker, SubFactory
from factory.django import DjangoModelFactory

from products.models import Product

User = get_user_model()

channel_choices = ("social", "search", "context", "email", "other")


class ProductFactory(DjangoModelFactory):
    """
    Factory for creating Product model instances with realistic test data.

    Generates random but realistic product data including:
    - Random product names using Faker's word generator
    - Descriptive text up to 300 characters
    - Positive decimal cost values with 4 integer and 2 decimal digits
    - Active status set to True by default

    Uses django_get_or_create on name field to prevent duplicate products
    with the same name in the database.
    """

    class Meta:
        """Metadata configuration for the ProductFactory."""

        model = Product
        django_get_or_create = ("name",)

    name = Faker("word")
    description = Faker("text", max_nb_chars=300)
    cost = Faker("pydecimal", left_digits=4, right_digits=2, positive=True)
    is_active = True


class AdvertisementFactory(DjangoModelFactory):
    """
    Factory for creating Advertisement model instances.

    Generates advertisement data with:
    - Random company names
    - Random selection from available marketing channels
    - Cost values with 5 integer and 2 decimal digits
    - Associated Product instance via SubFactory
    - Active status set to True by default
    """

    class Meta:
        model = "advertisements.Advertisement"

    name = Faker("company")
    channel = Faker("random_element", elements=channel_choices)
    cost = Faker("pydecimal", left_digits=5, right_digits=2, positive=True)
    product = SubFactory(ProductFactory)
    is_active = True


class LeadFactory(DjangoModelFactory):
    """
    Factory for creating Lead model instances with realistic personal data.

    Generates lead information including:
    - Random first, last, and middle names
    - Random phone numbers in various formats
    - Valid email addresses
    - Associated Advertisement instance via SubFactory
    """

    class Meta:
        model = "leads.Lead"

    first_name = Faker("first_name")
    last_name = Faker("last_name")
    middle_name = Faker("first_name")
    phone = Faker("phone_number")
    email = Faker("email")
    advertisement = SubFactory(AdvertisementFactory)


class ContractFactory(DjangoModelFactory):
    """
    Factory for creating Contract model instances with comprehensive contract data.

    Generates contract information including:
    - Random 3-word sentence for contract name
    - Associated Product instance
    - Mock document file (Word document with dummy content)
    - Realistic date ranges (start date this year, end date within next year)
    - Cost values with 6 integer and 2 decimal digits
    """

    class Meta:
        model = "contracts.Contract"

    name = Faker("sentence", nb_words=3)
    product = SubFactory(ProductFactory)
    document = SimpleUploadedFile(
        "contract.doc", b"file_content", content_type="application/msword"
    )
    start_date = Faker("date_this_year")
    end_date = Faker("date_between", start_date="+1d", end_date="+1y")
    cost = Faker("pydecimal", left_digits=6, right_digits=2, positive=True)


class CustomerFactory(DjangoModelFactory):
    """
    Factory for creating Customer model instances.

    Creates customer records by associating:
    - A Lead instance via SubFactory
    - A Contract instance via SubFactory

    Represents the final conversion of a lead to a customer with a signed contract.
    """

    class Meta:
        model = "customers.Customer"

    lead = SubFactory(LeadFactory)
    contract = SubFactory(ContractFactory)


class UserFactory(DjangoModelFactory):
    """
    Factory for creating Django User model instances for testing purposes.

    Generates user accounts with:
    - Random names for usernames
    - Random passwords
    - Non-superuser status by default

    Essential for testing authentication and authorization scenarios.
    """

    class Meta:
        """Metadata configuration for the UserFactory."""

        model = User

    username = Faker("name")
    password = Faker("password")
    is_superuser = False
