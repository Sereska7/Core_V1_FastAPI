"""Lifespan function."""

import asyncio
from contextlib import asynccontextmanager

from dependency_injector.wiring import inject
from fastapi import FastAPI


@inject
@asynccontextmanager
async def lifespan(
    app: FastAPI,  # pylint: disable=unused-argument
):
    app.state.shutting_down = False
    yield
    await shutdown_event()


async def shutdown_event() -> None:
    pending = [
        task for task in asyncio.all_tasks() if task is not asyncio.current_task()
    ]
    for task in pending:
        task.cancel()

    await asyncio.gather(*pending, return_exceptions=True)
