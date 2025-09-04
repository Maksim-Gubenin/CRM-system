from django.core.cache import cache
from typing import Any, Optional, Type, Callable
import hashlib
import json
from functools import wraps


class ModelCacheMixin:
    """Mixin для добавления методов кэширования к моделям с отладкой"""
    
    @classmethod
    def _get_cache_key(cls, pk: int) -> str:
        """Генерация ключа кэша для экземпляра модели"""
        return f"{cls.__name__.lower()}_{pk}"
    
    @classmethod
    def _get_queryset_cache_key(cls, suffix: str) -> str:
        """Генерация ключа кэша для QuerySet"""
        return f"{cls.__name__.lower()}_queryset_{suffix}"
    
    @classmethod
    def get_cached(cls, pk: int) -> Optional[Any]:
        """Получить объект из кэша по primary key"""
        cache_key = cls._get_cache_key(pk)
        cached_obj = cache.get(cache_key)
        
        if cached_obj:
            print(f"⚡ [CACHE HIT] {cache_key} - найден в кэше")
        else:
            print(f"❌ [CACHE MISS] {cache_key} - нет в кэше")
            
        return cached_obj
    
    @classmethod
    def get_or_set_cached(cls, pk: int, timeout: int = 300) -> Optional[Any]:
        """Получить объект из кэша или из БД и закэшировать"""
        cache_key = cls._get_cache_key(pk)
        print(f"🔍 [CACHE LOOKUP] Ищу {cache_key}")
        
        cached_obj = cls.get_cached(pk)
        if cached_obj is not None:
            return cached_obj
        
        print(f"🐌 [DB QUERY] {cache_key} - запрос к базе данных")
        try:
            obj = cls.objects.get(pk=pk)
            print(f"💾 [CACHE SET] {cache_key} - сохраняю в кэш (таймаут: {timeout}сек)")
            obj.set_cache(timeout=timeout)
            return obj
        except cls.DoesNotExist:
            print(f"🚫 [NOT FOUND] {cache_key} - объект не существует в БД")
            return None
    
    def set_cache(self, timeout: int = 300) -> None:
        """Сохранить объект в кэш"""
        cache_key = self._get_cache_key(self.pk)
        print(f"💾 [CACHE SET] {cache_key} - сохраняю в кэш")
        cache.set(cache_key, self, timeout=timeout)
    
    def invalidate_cache(self) -> None:
        """Удалить объект из кэша"""
        cache_key = self._get_cache_key(self.pk)
        print(f"🗑️ [CACHE INVALIDATE] {cache_key} - удаляю из кэша")
        cache.delete(cache_key)
    
    @classmethod
    def get_cached_queryset(cls, cache_key_suffix: str, queryset_func: Callable, 
                          timeout: int = 300, *args, **kwargs) -> Any:
        """Кэширование результатов QuerySet"""
        cache_key = cls._get_queryset_cache_key(cache_key_suffix)
        print(f"🔍 [QUERYSET CACHE] Ищу {cache_key}")
        
        result = cache.get(cache_key)
        
        if result is not None:
            print(f"⚡ [QUERYSET HIT] {cache_key} - найден в кэше")
            return result
        
        print(f"🐌 [QUERYSET MISS] {cache_key} - выполняю запрос к БД")
        result = queryset_func(*args, **kwargs)
        
        print(f"💾 [QUERYSET SET] {cache_key} - сохраняю в кэш")
        cache.set(cache_key, result, timeout=timeout)
        
        return result
    
    @classmethod
    def invalidate_queryset_cache(cls, cache_key_suffix: str) -> None:
        """Инвалидировать кэш конкретного QuerySet"""
        cache_key = cls._get_queryset_cache_key(cache_key_suffix)
        print(f"🗑️ [QUERYSET INVALIDATE] {cache_key} - удаляю из кэша")
        cache.delete(cache_key)
    
    @classmethod
    def bulk_invalidate_cache(cls, pks: list[int]) -> None:
        """Массовая инвалидация кэша для списка объектов"""
        print(f"🗑️ [BULK INVALIDATE] Удаляю кэш для {len(pks)} объектов")
        for pk in pks:
            cache_key = cls._get_cache_key(pk)
            cache.delete(cache_key)

from django.core.cache import cache
from typing import Any, Optional
import hashlib

from django.core.cache import cache
from typing import Any, Optional
import hashlib
from django.utils.decorators import method_decorator
from django.views.decorators.cache import cache_page

class ViewCacheMixin:
    """Mixin для кэширования View классов"""
    
    cache_timeout = 300  # 5 минут по умолчанию
    
    def get_cache_key(self) -> str:
        """Генерация уникального ключа кэша для View"""
        request = self.request
        path = request.get_full_path()
        user_id = request.user.id if request.user.is_authenticated else 'anonymous'
        language = getattr(request, 'LANGUAGE_CODE', 'en')
        return f"view_{self.__class__.__name__}_{user_id}_{language}_{hashlib.md5(path.encode()).hexdigest()}"
    
    def get_cached_response(self) -> Optional[Any]:
        """Получить закэшированный response"""
        cache_key = self.get_cache_key()
        return cache.get(cache_key)
    
    def cache_response(self, response: Any) -> None:
        """Сохранить response в кэш"""
        # Убеждаемся, что response рендерится перед кешированием
        if not response.is_rendered:
            response.render()
        
        cache_key = self.get_cache_key()
        cache.set(cache_key, response, self.cache_timeout)
    
    def dispatch(self, request, *args, **kwargs):
        # Проверяем кэш только для GET запросов
        if request.method == 'GET':
            cached_response = self.get_cached_response()
            if cached_response:
                print(f"⚡ [VIEW CACHE HIT] {self.get_cache_key()}")
                return cached_response
            
            print(f"❌ [VIEW CACHE MISS] {self.get_cache_key()}")
        
        response = super().dispatch(request, *args, **kwargs)
        
        if request.method == 'GET' and response.status_code == 200:
            self.cache_response(response)
            print(f"💾 [VIEW CACHE SET] {self.get_cache_key()}")
        
        return response

def cache_method(timeout: int = 300):
    """Декоратор для кэширования методов моделей с отладкой"""
    def decorator(func):
        @wraps(func)
        def wrapper(self, *args, **kwargs):
            cache_key = generate_cache_key(
                f"{self.__class__.__name__}_{func.__name__}_{self.pk}",
                *args,
                **kwargs
            )
            
            print(f"🔍 [METHOD CACHE] Ищу {cache_key}")
            result = cache.get(cache_key)
            
            if result is not None:
                print(f"⚡ [METHOD HIT] {cache_key} - найден в кэше")
                return result
            
            print(f"🐌 [METHOD MISS] {cache_key} - вычисляю результат")
            result = func(self, *args, **kwargs)
            
            print(f"💾 [METHOD SET] {cache_key} - сохраняю в кэш")
            cache.set(cache_key, result, timeout=timeout)
            
            return result
        return wrapper
    return decorator


def generate_cache_key(prefix: str, *args, **kwargs) -> str:
    """Генерация уникального ключа кэша на основе аргументов"""
    key_parts = [prefix]
    
    for arg in args:
        key_parts.append(str(arg))
    
    for key, value in sorted(kwargs.items()):
        key_parts.append(f"{key}_{value}")
    
    key_string = "_".join(key_parts)
    return hashlib.md5(key_string.encode()).hexdigest()
