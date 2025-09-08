import logging
from io import StringIO

from django.test import RequestFactory, TestCase

from crm.mixins import (
    LoggingMixin,
)
from crm.utils.factories import UserFactory


class TestLoggingMixin(TestCase):
    """Test cases for LoggingMixin"""

    def setUp(self):
        self.mixin = LoggingMixin()
        self.factory = RequestFactory()
        self.user = UserFactory()

    def test_get_client_ip_with_x_forwarded_for(self):
        """Test IP extraction from X-Forwarded-For header"""
        request = self.factory.get("/")
        request.META["HTTP_X_FORWARDED_FOR"] = "192.168.1.1, 10.0.0.1"

        ip = self.mixin.get_client_ip(request)
        self.assertEqual(ip, "192.168.1.1")

    def test_get_client_ip_with_remote_addr(self):
        """Test IP extraction from REMOTE_ADDR"""
        request = self.factory.get("/")
        request.META["REMOTE_ADDR"] = "192.168.1.2"

        ip = self.mixin.get_client_ip(request)
        self.assertEqual(ip, "192.168.1.2")

    def test_log_action_with_custom_handler(self):
        """Test that log_action works correctly"""
        # Capture logs
        log_stream = StringIO()
        handler = logging.StreamHandler(log_stream)
        logger = logging.getLogger("crm.mixins")
        logger.addHandler(handler)
        logger.setLevel(logging.INFO)

        try:
            self.mixin.log_action("info", "Test message %s", "test")
            log_contents = log_stream.getvalue()
            self.assertIn("Test message test", log_contents)
        finally:
            logger.removeHandler(handler)
