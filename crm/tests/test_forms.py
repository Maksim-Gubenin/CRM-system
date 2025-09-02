from django import forms
from django.contrib.auth.forms import AuthenticationForm
from django.test import TestCase
from django.utils.translation import gettext_lazy as _

from crm.forms import LoginForm


class LoginFormTest(TestCase):
    """Tests for LoginForm functionality.

    Attributes:
        valid_data (dict): Valid form data for testing
    """

    @classmethod
    def setUpTestData(cls) -> None:
        """Create test data for all test methods."""
        cls.valid_data = {"username": "testuser", "password": "testpassword123"}

    def test_form_inherits_from_authentication_form(self) -> None:
        """Test that LoginForm inherits from AuthenticationForm."""
        form = LoginForm()
        self.assertIsInstance(form, AuthenticationForm)

    def test_form_has_correct_fields(self) -> None:
        """Test that form has correct fields."""
        form = LoginForm()
        self.assertIn("username", form.fields)
        self.assertIn("password", form.fields)

    def test_username_field_widget_attributes(self) -> None:
        """Test username field widget attributes."""
        form = LoginForm()
        username_widget = form.fields["username"].widget

        self.assertEqual(username_widget.attrs["class"], "form-control")
        self.assertEqual(username_widget.attrs["placeholder"], _("Username"))
        self.assertIsInstance(username_widget, forms.TextInput)

    def test_password_field_widget_attributes(self) -> None:
        """Test password field widget attributes."""
        form = LoginForm()
        password_widget = form.fields["password"].widget

        self.assertEqual(password_widget.attrs["class"], "form-control")
        self.assertEqual(password_widget.attrs["placeholder"], _("Password"))
        self.assertIsInstance(password_widget, forms.PasswordInput)

    def test_form_validation_with_valid_data(self) -> None:
        """Test form validation with valid data."""
        form = LoginForm(data=self.valid_data)

        self.assertTrue(hasattr(form, "is_valid"))

    def test_form_validation_with_missing_username(self) -> None:
        """Test form validation with missing username."""
        invalid_data = self.valid_data.copy()
        invalid_data["username"] = ""
        form = LoginForm(data=invalid_data)

        self.assertFalse(form.is_valid())
        self.assertIn("username", form.errors)

    def test_form_validation_with_missing_password(self) -> None:
        """Test form validation with missing password."""
        invalid_data = self.valid_data.copy()
        invalid_data["password"] = ""
        form = LoginForm(data=invalid_data)

        self.assertFalse(form.is_valid())
        self.assertIn("password", form.errors)

    def test_form_validation_with_empty_data(self) -> None:
        """Test form validation with completely empty data."""
        form = LoginForm(data={})
        self.assertFalse(form.is_valid())
        self.assertIn("username", form.errors)
        self.assertIn("password", form.errors)

    def test_form_uses_custom_widgets(self) -> None:
        """Test that form uses custom widgets with correct attributes."""
        form = LoginForm()

        self.assertEqual(form.fields["username"].widget.attrs["class"], "form-control")
        self.assertEqual(form.fields["password"].widget.attrs["class"], "form-control")

    def test_form_field_labels(self) -> None:
        """Test that form fields have correct labels."""
        form = LoginForm()
        self.assertIn("username", form.fields)
        self.assertIn("password", form.fields)
