from django.core.cache import cache
def clear_cache():
    cache._cache.clear()
    cache._expire_info.clear()
