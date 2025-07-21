import logging
import sys
from functools import wraps
from datetime import datetime
from typing import Callable, Any, Coroutine

LOG_FORMAT = (
    "%(asctime)s | %(levelname)-8s | %(name)s | %(message)s"
)
DATE_FORMAT = "%Y-%m-%d %H:%M:%S"


def configure_logging(level: str = "INFO") -> None:
    """Configure root logging once at startup."""
    if logging.getLogger().handlers:
        # Already configured
        return

    logging.basicConfig(
        level=level.upper(),
        format=LOG_FORMAT,
        datefmt=DATE_FORMAT,
        stream=sys.stdout,
    )

    # Reduce noisy loggers if desired
    for noisy in [
        "pymongo",
        "motor",
        "asyncio",
        "uvicorn.error",
        "uvicorn.access",
    ]:
        logging.getLogger(noisy).setLevel(logging.WARNING)


def log_async(name: str | None = None) -> Callable[[Callable[..., Coroutine[Any, Any, Any]]], Callable[..., Coroutine[Any, Any, Any]]]:
    """Decorator that logs entry/exit + execution time of async functions."""

    def decorator(func):
        logger = logging.getLogger(name or func.__module__)

        @wraps(func)
        async def wrapper(*args, **kwargs):
            start = datetime.utcnow()
            logger.debug(f"➡️  START {func.__name__}")
            try:
                result = await func(*args, **kwargs)
                elapsed = (datetime.utcnow() - start).total_seconds() * 1000
                logger.debug(f"✅ END   {func.__name__} [{elapsed:.1f} ms]")
                return result
            except Exception:
                logger.exception(f"❌ ERROR in {func.__name__}")
                raise

        return wrapper

    return decorator 