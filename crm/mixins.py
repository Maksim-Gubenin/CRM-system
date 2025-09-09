import logging
import time
from collections import defaultdict
from typing import Any, TypeVar

from django import forms
from django.contrib import messages
from django.db import models
from django.db.models.deletion import ProtectedError
from django.http import HttpRequest, HttpResponse
from django.shortcuts import redirect
from django.utils.translation import gettext_lazy as _

logger = logging.getLogger(__name__)

_MT = TypeVar("_MT", bound=models.Model)
_FormT = TypeVar("_FormT", bound=forms.Form)
_SelfT = TypeVar("_SelfT", bound="LoggingMixin")


class LoggingMixin:
    """Mixin for logging actions in Class-Based Views.

    Provides comprehensive logging capabilities for Django views including
    request tracking, user identification, and IP address logging.
    """

    def get_client_ip(self, request: HttpRequest) -> str:
        """Extract client IP address from request headers.

        Args:
            request: HttpRequest object

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
        """Universal logging method with flexible level support.

        Args:
            level: Logging level (debug, info, warning, error, critical)
            message: Log message format string
            *args: Format arguments for the message
            **kwargs: Additional logging parameters
        """
        log_method = getattr(logger, level)
        formatted_message = message % args if args else message
        log_method(formatted_message, **kwargs)

    def dispatch(
        self: _SelfT, request: HttpRequest, *args: Any, **kwargs: Any
    ) -> HttpResponse:
        """Log all incoming requests with user and IP information.

        Args:
            request: HttpRequest object
            *args: Additional positional arguments
            **kwargs: Additional keyword arguments

        Returns:
            HttpResponse: Response from parent dispatch method
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

        return super().dispatch(request, *args, **kwargs)


class CreateLoggingMixin(LoggingMixin):
    """Mixin for logging object creation operations in CreateView."""

    def form_valid(self, form: _FormT) -> HttpResponse:
        """Log successful object creation with user information.

        Args:
            form: Validated form instance

        Returns:
            HttpResponse: Response from parent form_valid method
        """
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
        """Log form validation failures with error details.

        Args:
            form: Invalid form instance

        Returns:
            HttpResponse: Response from parent form_invalid method
        """
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
    """Mixin for logging object update operations in UpdateView."""

    def form_valid(self, form: _FormT) -> HttpResponse:
        """Log successful object update with before/after comparison.

        Args:
            form: Validated form instance

        Returns:
            HttpResponse: Response from parent form_valid method
        """
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
        """Log form validation failures for update operations.

        Args:
            form: Invalid form instance

        Returns:
            HttpResponse: Response from parent form_invalid method
        """
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
    """Mixin for logging object deletion operations in DeleteView."""

    def delete(self, request: HttpRequest, *args: Any, **kwargs: Any) -> HttpResponse:
        """Log object deletion with user information.

        Args:
            request: HttpRequest object
            *args: Additional positional arguments
            **kwargs: Additional keyword arguments

        Returns:
            HttpResponse: Response from parent delete method
        """
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
    """Mixin for logging object detail view operations in DetailView."""

    def get(self, request: HttpRequest, *args: Any, **kwargs: Any) -> HttpResponse:
        """Log object detail view access with user information.

        Args:
            request: HttpRequest object
            *args: Additional positional arguments
            **kwargs: Additional keyword arguments

        Returns:
            HttpResponse: Response from parent get method
        """
        obj = self.get_object()
        self.log_action(
            "info",
            "Object viewed: %s by user %s",
            str(obj),
            request.user.username if request.user.is_authenticated else "anonymous",
        )
        return super().get(request, *args, **kwargs)


class ListLoggingMixin(LoggingMixin):
    """Mixin for logging list view operations in ListView."""

    def get(self, request: HttpRequest, *args: Any, **kwargs: Any) -> HttpResponse:
        """Log list view access with object count and user information.

        Args:
            request: HttpRequest object
            *args: Additional positional arguments
            *kwargs: Additional keyword arguments

        Returns:
            HttpResponse: Response from parent get method
        """
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

    # pylint: disable=too-few-public-methods
    def dispatch(self, request: HttpRequest, *args: Any, **kwargs: Any) -> HttpResponse:
        """Measure and log view execution time in seconds.

        Args:
            request: HttpRequest object
            *args: Additional positional arguments
            **kwargs: Additional keyword arguments

        Returns:
            HttpResponse: Response from parent dispatch method
        """
        start_time = time.time()
        response = super().dispatch(request, *args, **kwargs)
        end_time = time.time()

        logger.debug(
            "%s executed in %.3f seconds",
            self.__class__.__name__,
            end_time - start_time,
        )
        return response


class ProtectedErrorMixin:
    """Mixin for handling ProtectedError in DeleteView operations.

    Prevents application crashes when attempting to delete objects
    with protected foreign key relationships.
    """

    def get_protected_error_message(self, protected_error: ProtectedError) -> str:
        """Generate user-friendly error message for protected objects.

        Args:
            protected_error: ProtectedError exception instance

        Returns:
            str: Formatted error message with object details
        """
        protected_objects = list(protected_error.protected_objects)

        object_groups = defaultdict(list)

        for obj in protected_objects:
            model_name = obj._meta.verbose_name
            object_groups[model_name].append(f"#{obj.pk}")

        # Create readable message
        details = []
        for model_name, ids in object_groups.items():
            if len(ids) <= 3:
                details.append(f"{model_name} {', '.join(ids)}")
            else:
                details.append(f"{model_name} ({len(ids)} objects)")

        return _(
            "Cannot delete '%(object_name)s' "
            "because it is linked to other objects: %(details)s. "
            "Please remove or reassign these objects first."
        ) % {"object_name": str(self.object), "details": "; ".join(details)}

    def handle_protected_error(
        self, request: HttpRequest, protected_error: ProtectedError
    ) -> HttpResponse:
        """Handle ProtectedError by showing user message and redirecting.

        Args:
            request: HttpRequest object
            protected_error: ProtectedError exception instance

        Returns:
            HttpResponse: Redirect response to appropriate page
        """
        error_message = self.get_protected_error_message(protected_error)
        messages.error(request, error_message)

        # Return to appropriate page
        if hasattr(self.object, "get_absolute_url"):
            return redirect(self.object.get_absolute_url())
        if hasattr(self, "get_success_url"):
            return redirect(self.get_success_url())
        return redirect("../")  # Go one level up

    def form_valid(self, form: _FormT) -> HttpResponse:
        """Intercept ProtectedError during object deletion.

        Args:
            form: Form instance

        Returns:
            HttpResponse: Response from parent method or error handling
        """
        try:
            return super().form_valid(form)
        except ProtectedError as e:
            return self.handle_protected_error(self.request, e)
