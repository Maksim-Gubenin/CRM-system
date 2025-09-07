import hashlib
from functools import wraps
from typing import Any, Callable, Optional, TypeVar, cast

from django.core.cache import cache
from django.db import models

M = TypeVar("M", bound=models.Model)


class ModelCacheMixin:
    """Mixin for adding caching methods to Django models.

    Provides caching capabilities for model instances and querysets with
    automatic cache key generation and invalidation.
    """

    @classmethod
    def _get_cache_key(cls, pk: int) -> str:
        """Generate cache key for model instance.

        Args:
            pk: Primary key of the model instance

        Returns:
            str: Cache key in format 'modelname_pk'
        """
        return f"{cls.__name__.lower()}_{pk}"

    @classmethod
    def _get_queryset_cache_key(cls, suffix: str) -> str:
        """Generate cache key for queryset.

        Args:
            suffix: Unique identifier for the queryset

        Returns:
            str: Cache key in format 'modelname_queryset_suffix'
        """
        return f"{cls.__name__.lower()}_queryset_{suffix}"

    @classmethod
    def get_cached(cls: type[M], pk: int) -> Any:
        """Retrieve object from cache by primary key.

        Args:
            pk: Primary key of the model instance

        Returns:
            Optional[Any]: Cached object or None if not found
        """
        cache_key = cls._get_cache_key(pk)
        return cache.get(cache_key)

    @classmethod
    def get_or_set_cached(cls: type[M], pk: int, timeout: int = 300) -> Any:
        """Retrieve object from cache or database and cache it.

        Args:
            pk: Primary key of the model instance
            timeout: Cache timeout in seconds (default: 300)

        Returns:
            Optional[Any]: Model instance or None if not found
        """
        cls._get_cache_key(pk)

        cached_obj = cls.get_cached(pk)
        if cached_obj is not None:
            return cached_obj

        try:
            model_cls = cast(models.Model, cls)
            obj = model_cls.objects.get(pk=pk)
            obj.set_cache(timeout=timeout)
            return obj
        except model_cls.DoesNotExist:  # type: ignore
            return None

    def set_cache(self: M, timeout: int = 300) -> None:
        """Save object to cache.

        Args:
            timeout: Cache timeout in seconds (default: 300)
        """
        cache_key = self._get_cache_key(self.pk)  # type: ignore
        cache.set(cache_key, self, timeout=timeout)

    def invalidate_cache(self: M) -> None:
        """Remove object from cache."""
        cache_key = self._get_cache_key(self.pk)  # type: ignore
        cache.delete(cache_key)

    @classmethod
    def get_cached_queryset(
        cls: type[M],
        cache_key_suffix: str,
        queryset_func: Callable[..., Any],
        *args: Any,
        timeout: int = 300,
        **kwargs: Any,
    ) -> Any:
        """Cache and retrieve queryset results.

        Args:
            cache_key_suffix: Unique identifier for the queryset
            queryset_func: Function that returns the queryset
            *args: Positional arguments for queryset_func
            timeout: Cache timeout in seconds (default: 300)
            **kwargs: Keyword arguments for queryset_func

        Returns:
            Any: Cached queryset results
        """
        cache_key = cls._get_queryset_cache_key(cache_key_suffix)

        result = cache.get(cache_key)
        if result is not None:
            return result

        result = queryset_func(*args, **kwargs)
        cache.set(cache_key, result, timeout=timeout)

        return result

    @classmethod
    def invalidate_queryset_cache(cls: type[M], cache_key_suffix: str) -> None:
        """Invalidate cache for specific queryset.

        Args:
            cache_key_suffix: Unique identifier for the queryset
        """
        cache_key = cls._get_queryset_cache_key(cache_key_suffix)
        cache.delete(cache_key)

    @classmethod
    def bulk_invalidate_cache(cls: type[M], pks: list[int]) -> None:
        """Bulk invalidate cache for multiple objects.

        Args:
            pks: List of primary keys to invalidate
        """
        for pk in pks:
            cache_key = cls._get_cache_key(pk)
            cache.delete(cache_key)


class ViewCacheMixin:
    """Mixin for caching Django View responses with Redis support.

    Provides response caching for GET requests with automatic cache key
    generation based on request path, user, and language.
    """

    cache_timeout = 300

    def get_cache_key(self) -> str:
        """Generate unique cache key for View with prefix.

        Returns:
            str: Cache key including class name, user, language, and path hash
        """
        request = self.request  # type: ignore
        path = request.get_full_path()
        user_id = request.user.id if request.user.is_authenticated else "anonymous"
        language = getattr(request, "LANGUAGE_CODE", "en")

        base_key = (
            f"view:{self.__class__.__name__}:{user_id}:{language}:"
            f"{hashlib.md5(path.encode()).hexdigest()}"
        )
        return f"crm:{base_key}"

    def get_cached_response(self) -> Optional[Any]:
        """Retrieve cached response.

        Returns:
            Optional[Any]: Cached HttpResponse or None
        """
        cache_key = self.get_cache_key()
        return cache.get(cache_key)

    def cache_response(self, response: Any) -> None:
        """Save response to cache.

        Args:
            response: HttpResponse to cache
        """
        if not response.is_rendered:
            response.render()

        cache_key = self.get_cache_key()
        cache.set(cache_key, response, self.cache_timeout)

    def dispatch(self, request: Any, *args: Any, **kwargs: Any) -> Any:
        """Override dispatch method to handle caching."""
        if request.method == "GET":
            cached_response = self.get_cached_response()
            if cached_response is not None:
                return cached_response

        response = super().dispatch(request, *args, **kwargs)  # type: ignore

        if request.method == "GET" and response.status_code == 200:
            self.cache_response(response)

        return response


class ViewCacheInvalidationMixin:
    """Mixin for invalidating View cache with Redis pattern matching support.

    Provides methods to invalidate cached responses for specific views
    or patterns using Redis pattern matching capabilities.
    """

    def invalidate_view_cache(self, view_classes: Optional[list[str]] = None) -> None:
        """Invalidate cache for specified View classes using Redis pattern matching.

        Args:
            view_classes: List of View class names to invalidate, or None for all
        """
        request = self.request  # type: ignore
        user_id = request.user.id if request.user.is_authenticated else "anonymous"
        language = getattr(request, "LANGUAGE_CODE", "en")

        if view_classes is None:
            pattern = f"crm:view:*:{user_id}:{language}:*"
            self._invalidate_by_pattern(pattern)
        else:
            for view_class in view_classes:
                pattern = f"crm:view:{view_class}:{user_id}:{language}:*"
                self._invalidate_by_pattern(pattern)

    def _invalidate_by_pattern(self, pattern: str) -> None:
        """Invalidate all cache keys matching the pattern.

        Args:
            pattern: Redis pattern to match keys against
        """
        try:
            keys = cache.keys(pattern)
            if keys:
                cache.delete_many(keys)
        except (AttributeError, ValueError):  # More specific exception handling
            # Fallback to clear cache if pattern matching fails
            cache.clear()

    def invalidate_object_cache(self, obj: Any) -> None:
        """Invalidate model object cache.

        Args:
            obj: Model instance with invalidate_cache method
        """
        if hasattr(obj, "invalidate_cache"):
            obj.invalidate_cache()


def cache_method(timeout: int = 300) -> Callable:
    """Decorator for caching model methods.

    Args:
        timeout: Cache timeout in seconds (default: 300)

    Returns:
        Callable: Decorated method with caching
    """

    def decorator(func: Callable) -> Callable:
        @wraps(func)
        def wrapper(self: Any, *args: Any, **kwargs: Any) -> Any:
            cache_key = generate_cache_key(
                f"{self.__class__.__name__}_" f"{func.__name__}_{self.pk}",
                *args,
                **kwargs,  # type: ignore
            )

            result = cache.get(cache_key)
            if result is not None:
                return result

            result = func(self, *args, **kwargs)
            cache.set(cache_key, result, timeout=timeout)

            return result

        return wrapper

    return decorator


def generate_cache_key(prefix: str, *args: Any, **kwargs: Any) -> str:
    """Generate unique cache key based on arguments.

    Args:
        prefix: Base prefix for the cache key
        *args: Positional arguments to include in key
        **kwargs: Keyword arguments to include in key

    Returns:
        str: MD5 hash of the generated key string
    """
    key_parts = [prefix]

    for arg in args:
        key_parts.append(str(arg))

    for key, value in sorted(kwargs.items()):
        key_parts.append(f"{key}_{value}")

    key_string = "_".join(key_parts)
    return hashlib.md5(key_string.encode()).hexdigest()
