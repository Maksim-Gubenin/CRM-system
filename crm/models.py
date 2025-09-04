from django.db import models
from django.utils.translation import gettext_lazy as _

from crm.cache import ModelCacheMixin  # Импортируем миксин


class BaseModel(models.Model, ModelCacheMixin):
    """Abstract base model with common fields, methods and caching.

    Provides:
    - created_at (DateTime): When the instance was created
    - updated_at (DateTime): When the instance was last updated
    - Automatic caching functionality with debug prints
    """

    class Meta:
        abstract = True

    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name=_("Created at"),
        help_text=_("When the %(class)s was created"),
    )

    updated_at = models.DateTimeField(
        auto_now=True,
        verbose_name=_("Updated at"),
        help_text=_("When the %(class)s was last updated"),
    )

    def save(self, *args, **kwargs):
        """Override save to handle caching with debug"""
        print(f"💾 [SAVE] Сохраняю {self.__class__.__name__} id={getattr(self, 'pk', 'NEW')}")
        is_new = self.pk is None
        
        # Сохраняем объект
        result = super().save(*args, **kwargs)
        
        if not is_new:
            print(f"🔄 [UPDATE] Обновляю кэш для существующего объекта")
            self.invalidate_cache()  # Сначала инвалидируем старый кэш
        
        # Сохраняем в кэш после сохранения в БД
        self.set_cache()
        
        return result

    def delete(self, *args, **kwargs):
        """Override delete to handle caching with debug"""
        print(f"🗑️ [DELETE] Удаляю {self.__class__.__name__} id={self.pk}")
        
        # Инвалидируем кэш перед удалением из БД
        self.invalidate_cache()
        
        # Удаляем объект из БД
        return super().delete(*args, **kwargs)

    def __str__(self):
        """String representation with cache info"""
        pk = getattr(self, 'pk', None)
        if pk:
            cache_key = self._get_cache_key(pk)
            is_cached = cache.get(cache_key) is not None
            cache_status = "⚡" if is_cached else "❌"
            return f"{cache_status} {self.__class__.__name__}(id={pk})"
        return f"🆕 {self.__class__.__name__}(NEW)"