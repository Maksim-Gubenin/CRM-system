import logging
import time
from io import StringIO

from django.contrib.auth.models import AnonymousUser
from django.http import HttpResponse
from django.test import RequestFactory, TestCase

from crm.decorators import log_view_action
from crm.utils.factories import UserFactory


class TestLogViewActionDecorator(TestCase):
    """Test cases for log_view_action decorator"""

    def setUp(self):
        self.factory = RequestFactory()
        self.user = UserFactory()
        self.log_stream = StringIO()
        self.handler = logging.StreamHandler(self.log_stream)

        # Configure logger to capture output
        logger = logging.getLogger("crm.decorators")
        logger.addHandler(self.handler)
        logger.setLevel(logging.INFO)

    def tearDown(self):
        # Clean up logger
        logger = logging.getLogger("crm.decorators")
        logger.removeHandler(self.handler)

    def test_log_view_action_with_authenticated_user(self):
        """Test decorator logs access by authenticated user"""

        @log_view_action("test_view")
        def test_view(request):
            return HttpResponse("OK")

        request = self.factory.get("/test/")
        request.user = self.user

        response = test_view(request)

        log_contents = self.log_stream.getvalue()
        self.assertIn(
            f"View test_view accessed by user {self.user.username}", log_contents
        )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.content.decode(), "OK")

    def test_log_view_action_with_anonymous_user(self):
        """Test decorator logs access by anonymous user"""

        @log_view_action("test_view")
        def test_view(request):
            return HttpResponse("OK")

        request = self.factory.get("/test/")
        request.user = AnonymousUser()

        response = test_view(request)

        log_contents = self.log_stream.getvalue()
        self.assertIn("View test_view accessed by user anonymous", log_contents)
        self.assertEqual(response.status_code, 200)

    def test_log_view_action_without_custom_name(self):
        """Test decorator uses function name when no custom name provided"""

        @log_view_action()
        def test_function_view(request):
            return HttpResponse("OK")

        request = self.factory.get("/test/")
        request.user = self.user

        response = test_function_view(request)

        log_contents = self.log_stream.getvalue()
        self.assertIn("View test_function_view accessed by user", log_contents)
        self.assertEqual(response.status_code, 200)

    def test_log_view_action_execution_time_logged(self):
        """Test decorator logs execution time at debug level"""

        # Set up debug logging
        logger = logging.getLogger("crm.decorators")
        logger.setLevel(logging.DEBUG)

        @log_view_action("slow_view")
        def slow_view(request):
            # Small delay to ensure measurable execution time

            time.sleep(0.001)
            return HttpResponse("OK")

        request = self.factory.get("/test/")
        request.user = self.user

        response = slow_view(request)

        log_contents = self.log_stream.getvalue()
        self.assertIn("View slow_view executed in", log_contents)
        self.assertEqual(response.status_code, 200)

    def test_log_view_action_preserves_function_arguments(self):
        """Test decorator preserves all function arguments and keyword arguments"""

        @log_view_action("args_view")
        def args_view(request, arg1, arg2, kwarg1=None, kwarg2=None):
            return HttpResponse(f"{arg1}_{arg2}_{kwarg1}_{kwarg2}")

        request = self.factory.get("/test/")
        request.user = self.user

        response = args_view(request, "val1", "val2", kwarg1="kw1", kwarg2="kw2")

        log_contents = self.log_stream.getvalue()
        self.assertIn("View args_view accessed by user", log_contents)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.content.decode(), "val1_val2_kw1_kw2")

    def test_log_view_action_with_different_http_methods(self):
        """Test decorator works with different HTTP methods"""

        @log_view_action("method_view")
        def method_view(request):
            return HttpResponse(request.method)

        request = self.factory.post("/test/")
        request.user = self.user

        response = method_view(request)

        log_contents = self.log_stream.getvalue()
        self.assertIn("View method_view accessed by user", log_contents)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.content.decode(), "POST")
