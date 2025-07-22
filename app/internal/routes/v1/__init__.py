"""Routes for version 1 of the API."""

from fastapi import APIRouter

from app.internal.routes.v1.user import router as user_router

router = APIRouter(
    prefix="/v1",
)

routes = sorted(
    [user_router],
    key=lambda r: r.prefix,
)

for route in routes:
    router.include_router(route)
