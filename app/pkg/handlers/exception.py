"""Handler exception module."""

import asyncio
import functools

from app.pkg.logger import get_logger

logger = get_logger(__name__)


def handle_cancelled_error(func):
    @functools.wraps(func)
    async def wrapper(*args, **kwargs):
        try:
            return await func(*args, **kwargs)
        except asyncio.CancelledError:
            raise

    return wrapper
