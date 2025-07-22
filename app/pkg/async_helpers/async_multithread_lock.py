"""This module contains a class for locking."""

import asyncio
import contextlib
import multiprocessing
from concurrent import futures


class AsyncMultiprocessingLock:
    """This class is used for locking both async and multiprocess apps.

    You can easily adapt it from multithreading. Just set self._lock = threading.Lock()

    Use preload=True for gunicorn for classes to init their locks,
        so they are shared between the processes.
    threading.Lock locks always no matter if it's async or another thread
    but for async it should not block the loop.

    Be careful, threading.Lock does not lock processes even if it is shared between them

    Source: https://stackoverflow.com/a/63425191
    """

    _pool = futures.ThreadPoolExecutor()

    def __init__(self) -> None:
        self._lock = multiprocessing.Lock()

    @contextlib.asynccontextmanager
    async def async_lock(self) -> None:
        """Use inside async methods as 'async with object.async_lock():'."""
        loop = asyncio.get_event_loop()

        await loop.run_in_executor(self._pool, self._lock.acquire)

        try:
            yield  # the lock is held
        finally:
            self._lock.release()

    @contextlib.contextmanager
    def lock(self) -> None:
        """Use inside sync methods as 'with object.lock():'."""

        with self._lock:
            try:
                yield  # the lock is held
            finally:
                pass
