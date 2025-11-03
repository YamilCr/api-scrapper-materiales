import asyncio
import logging

logger = logging.getLogger(__name__)

def with_timeout_and_log(timeout=20):
    def decorator(coro_func):
        async def wrapper(*args, **kwargs):
            try:
                return await asyncio.wait_for(coro_func(*args, **kwargs), timeout=timeout)
            except Exception as e:
                logger.warning(f"[fetch_all_products] Error en {coro_func.__name__}: {e}")
                return []
        return wrapper
    return decorator