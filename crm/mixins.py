# file: ignore

import logging
import time
from typing import Any, TypeVar

from django import forms
from django.db import models
from django.http import HttpRequest, HttpResponse

logger = logging.getLogger(__name__)

_MT = TypeVar("_MT", bound=models.Model)
_FormT = TypeVar("_FormT", bound=forms.Form)
_SelfT = TypeVar("_SelfT", bound="LoggingMixin")


class LoggingMixin:
    """Mixin for logging actions in CBV (Class-Based Views)."""

    def get_client_ip(self, request: HttpRequest) -> str:
        """Extract client IP address from request."""
        x_forwarded_for = request.META.get("HTTP_X_FORWARDED_FOR")
        if x_forwarded_for:
            ip = x_forwarded_for.split(",")[0]
        else:
            ip = request.META.get("REMOTE_ADDR", "unknown")
        return ip or "unknown"

    def log_action(self, level: str, message: str, *args: Any, **kwargs: Any) -> None:
        """Universal logging method."""
        log_method = getattr(logger, level)
        formatted_message = message % args if args else message
        log_method(formatted_message, **kwargs)

    def dispatch(
        self: _SelfT, request: HttpRequest, *args: Any, **kwargs: Any
    ) -> HttpResponse:
        """Log all incoming requests."""
        self.log_action(
            "info",
            "%s accessed by user %s (IP: %s)",
            self.__class__.__name__,
            request.user.username if request.user.is_authenticated else "anonymous",
            self.get_client_ip(request),
        )

        if request.method not in ["GET", "HEAD", "OPTIONS"]:
            request_data: dict[str, Any] = {}
            if hasattr(request, request.method):
                data_source = getattr(request, request.method)
                if isinstance(data_source, dict):
                    request_data = data_source
                elif hasattr(data_source, "dict"):
                    request_data = data_source.dict()

            self.log_action(
                "debug",
                "%s %s data: %s",
                request.method,
                self.__class__.__name__,
                request_data,
            )

        return super().dispatch(request, *args, **kwargs)


class CreateLoggingMixin(LoggingMixin):
    """Mixin for logging object creation operations."""

    def form_valid(self, form: _FormT) -> HttpResponse:
        """Log successful object creation."""
        result = super().form_valid(form)
        self.log_action(
            "info",
            "Object created: %s by user %s",
            str(self.object),
            (
                self.request.user.username
                if self.request.user.is_authenticated
                else "anonymous"
            ),
        )
        return result

    def form_invalid(self, form: _FormT) -> HttpResponse:
        """Log form validation failures."""
        self.log_action(
            "warning",
            "Create failed by user %s. Errors: %s",
            (
                self.request.user.username
                if self.request.user.is_authenticated
                else "anonymous"
            ),
            form.errors.as_json(),
        )
        return super().form_invalid(form)


class UpdateLoggingMixin(LoggingMixin):
    """Mixin for logging object update operations."""

    def form_valid(self, form: _FormT) -> HttpResponse:
        """Log successful object update."""
        old_object = self.get_object()
        result = super().form_valid(form)
        self.log_action(
            "info",
            "Object updated: %s -> %s by user %s",
            str(old_object),
            str(self.object),
            (
                self.request.user.username
                if self.request.user.is_authenticated
                else "anonymous"
            ),
        )
        return result

    def form_invalid(self, form: _FormT) -> HttpResponse:
        """Log form validation failures."""
        self.log_action(
            "warning",
            "Update failed for %s by user %s. Errors: %s",
            str(self.get_object()),
            (
                self.request.user.username
                if self.request.user.is_authenticated
                else "anonymous"
            ),
            form.errors.as_json(),
        )
        return super().form_invalid(form)


class DeleteLoggingMixin(LoggingMixin):
    """Mixin for logging object deletion operations."""

    def delete(self, request: HttpRequest, *args: Any, **kwargs: Any) -> HttpResponse:
        """Log object deletion."""
        obj = self.get_object()
        result = super().delete(request, *args, **kwargs)
        self.log_action(
            "warning",
            "Object deleted: %s by user %s",
            str(obj),
            request.user.username if request.user.is_authenticated else "anonymous",
        )
        return result


class DetailLoggingMixin(LoggingMixin):
    """Mixin for logging object detail view operations."""

    def get(self, request: HttpRequest, *args: Any, **kwargs: Any) -> HttpResponse:
        """Log object detail view access."""
        obj = self.get_object()
        self.log_action(
            "info",
            "Object viewed: %s by user %s",
            str(obj),
            request.user.username if request.user.is_authenticated else "anonymous",
        )
        return super().get(request, *args, **kwargs)


class ListLoggingMixin(LoggingMixin):
    """Mixin for logging list view operations."""

    def get(self, request: HttpRequest, *args: Any, **kwargs: Any) -> HttpResponse:
        """Log list view access with object count."""
        response = super().get(request, *args, **kwargs)

        context_data = getattr(response, "context_data", {})
        context_object_name = getattr(self, "context_object_name", "object_list")
        object_list = context_data.get(
            context_object_name, context_data.get("object_list", [])
        )

        count = len(object_list) if object_list else 0
        self.log_action(
            "info",
            "List viewed: %d objects by user %s",
            count,
            request.user.username if request.user.is_authenticated else "anonymous",
        )
        return response


class PerformanceLoggingMixin:
    """Mixin for performance monitoring and timing of view execution."""

    def dispatch(self, request: HttpRequest, *args: Any, **kwargs: Any) -> HttpResponse:
        """Measure and log view execution time."""
        start_time = time.time()
        response = super().dispatch(request, *args, **kwargs)
        end_time = time.time()

        logger.debug(
            "%s executed in %.3f seconds",
            self.__class__.__name__,
            end_time - start_time,
        )
        return response
