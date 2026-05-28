from django.core.cache import cache

def cache_key(user_id: int, query: str) -> str:
    """Generate a cache key for inline voice search."""
    return f"voice_search:{user_id}:{query.strip().lower()}"

def invalidate_inline_cache(user_id: int, query: str = ""):
    """Invalidate cached inline results for a specific user.
    If `query` is empty, only the generic key is removed; otherwise the specific key is cleared.
    """
    # Specific query cache
    cache.delete(cache_key(user_id, query))
    # General fallback (used when query is empty)
    cache.delete(f"voice_search:{user_id}:")
