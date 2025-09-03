import logging
import time
from functools import wraps
from typing import Any, Callable, Optional, TypeVar, cast

from django.http import HttpRequest, HttpResponse

logger = logging.getLogger(__name__)

F = TypeVar("F", bound=Callable[..., HttpResponse])
R = TypeVar("R")


def log_view_action(view_name: Optional[str] = None) -> Callable[[F], F]:
    """
    Decorator for logging actions in FBV (Function-Based Views).

    Logs view access information and execution time for performance monitoring.

    Args:
        view_name: Optional custom name for the view in logs.
                  If not provided, uses the function name.

    Returns:
        Callable[[F], F]: Decorated view function with logging capabilities.
    """

    def decorator(view_func: F) -> F:
        @wraps(view_func)
        def wrapped_view(
            request: HttpRequest, *args: Any, **kwargs: Any
        ) -> HttpResponse:
            name = view_name or view_func.__name__

            username = (
                request.user.username if request.user.is_authenticated else "anonymous"
            )
            logger.info("View %s accessed by user %s", name, username)

            start_time = time.time()
            response = view_func(request, *args, **kwargs)
            end_time = time.time()

            logger.debug(
                "View %s executed in %.3f seconds", name, end_time - start_time
            )

            return response

        return cast(F, wrapped_view)

    return decorator
