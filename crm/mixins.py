import logging
import time
from typing import Any, TypeVar, cast

from django import forms
from django.db import models
from django.http import HttpRequest, HttpResponse
from django.views import View
from django.views.generic import (
    CreateView,
    DeleteView,
    DetailView,
    ListView,
    UpdateView,
)

logger = logging.getLogger(__name__)

_MT = TypeVar("_MT", bound=models.Model)
_FormT = TypeVar("_FormT", bound=forms.Form)
_SelfT = TypeVar("_SelfT", bound="LoggingMixin")


class LoggingMixin:
    """
    Mixin for logging actions in CBV (Class-Based Views).

    Provides logging capabilities for Django class-based views including
    request logging, user authentication tracking, and IP address capture.
    """

    def get_client_ip(self, request: HttpRequest) -> str:
        """
        Extract client IP address from request for logging purposes.

        Args:
            request: HttpRequest object containing request metadata

        Returns:
            str: Client IP address or 'unknown' if not available
        """
        x_forwarded_for = request.META.get("HTTP_X_FORWARDED_FOR")
        if x_forwarded_for:
            ip = x_forwarded_for.split(",")[0]
        else:
            ip = request.META.get("REMOTE_ADDR", "unknown")
        return ip or "unknown"

    def log_action(self, level: str, message: str, *args: Any, **kwargs: Any) -> None:
        """
        Universal logging method that supports different log levels.

        Args:
            level: Log level (info, warning, error, debug, etc.)
            message: Log message with optional formatting placeholders
            *args: Positional arguments for message formatting
            **kwargs: Keyword arguments for logger method
        """
        log_method = getattr(logger, level)
        formatted_message = message % args if args else message
        log_method(formatted_message, **kwargs)

    def dispatch(
        self: _SelfT, request: HttpRequest, *args: Any, **kwargs: Any
    ) -> HttpResponse:
        """
        Log all incoming requests with user and IP information.

        For non-GET/HEAD/OPTIONS requests, also logs request data.
        """
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

        super_obj = super()
        if hasattr(super_obj, "dispatch"):
            return cast(HttpResponse, super_obj.dispatch(request, *args, **kwargs))

        return View.dispatch(cast(View, self), request, *args, **kwargs)


class CreateLoggingMixin(LoggingMixin):
    """
    Mixin for logging object creation operations.

    Logs successful object creation and form validation failures.
    """

    def form_valid(self: CreateView[_MT, _FormT], form: _FormT) -> HttpResponse:
        """Log successful object creation and return result."""
        result = super().form_valid(form)  # type: ignore
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

    def form_invalid(self: CreateView[_MT, _FormT], form: _FormT) -> HttpResponse:
        """Log form validation failures during object creation."""
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
        return super().form_invalid(form)  # type: ignore


class UpdateLoggingMixin(LoggingMixin):
    """
    Mixin for logging object update operations.

    Logs successful object updates and form validation failures.
    """

    def form_valid(self: UpdateView[_MT, _FormT], form: _FormT) -> HttpResponse:
        """Log successful object update and return result."""
        old_object = self.get_object()
        result = super().form_valid(form)  # type: ignore
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

    def form_invalid(self: UpdateView[_MT, _FormT], form: _FormT) -> HttpResponse:
        """Log form validation failures during object update."""
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
        return super().form_invalid(form)  # type: ignore


class DeleteLoggingMixin(LoggingMixin):
    """
    Mixin for logging object deletion operations.

    Logs successful object deletions with warning level.
    """

    def delete(
        self: DeleteView[_MT, _FormT], request: HttpRequest, *args: Any, **kwargs: Any
    ) -> HttpResponse:
        """Log object deletion and return result."""
        obj = self.get_object()
        result = super().delete(request, *args, **kwargs)  # type: ignore
        self.log_action(
            "warning",
            "Object deleted: %s by user %s",
            str(obj),
            request.user.username if request.user.is_authenticated else "anonymous",
        )
        return result


class DetailLoggingMixin(LoggingMixin):
    """
    Mixin for logging object detail view operations.

    Logs when users view detailed information about objects.
    """

    def get(
        self: DetailView[_MT], request: HttpRequest, *args: Any, **kwargs: Any
    ) -> HttpResponse:
        """Log object detail view access and return response."""
        obj = self.get_object()
        self.log_action(
            "info",
            "Object viewed: %s by user %s",
            str(obj),
            request.user.username if request.user.is_authenticated else "anonymous",
        )
        return super().get(request, *args, **kwargs)  # type: ignore


class ListLoggingMixin(LoggingMixin):
    """
    Mixin for logging list view operations.

    Logs when users view object lists and includes object count.
    """

    def get(
        self: ListView[_MT], request: HttpRequest, *args: Any, **kwargs: Any
    ) -> HttpResponse:
        """Log list view access with object count and return response."""
        response = super().get(request, *args, **kwargs)  # type: ignore

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
    """
    Mixin for performance monitoring and timing of view execution.

    Measures and logs execution time of view dispatch methods.
    """

    # pylint: disable=too-few-public-methods

    def dispatch(
        self: View, request: HttpRequest, *args: Any, **kwargs: Any
    ) -> HttpResponse:
        """Measure and log view execution time."""
        start_time = time.time()

        super_obj = super()
        if hasattr(super_obj, "dispatch"):
            response = cast(HttpResponse, super_obj.dispatch(request, *args, **kwargs))
        else:
            response = View.dispatch(cast(View, self), request, *args, **kwargs)

        end_time = time.time()

        logger.debug(
            "%s executed in %.3f seconds",
            self.__class__.__name__,
            end_time - start_time,
        )

        return response
