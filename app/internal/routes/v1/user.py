"""Routes for User module."""

from dependency_injector.wiring import Provide, inject
from fastapi import APIRouter, Depends, status

from app.internal.services import Services
from app.internal.services.v1 import UserService
from app.pkg.models import v1 as models
from app.pkg.models.base.request_id_route import RequestIDRoute

router = APIRouter(prefix="/user", tags=["User"], route_class=RequestIDRoute)


@router.get(
    "/",
    status_code=status.HTTP_200_OK,
    response_model=list[models.User],
    description="""
    Description: Get all User.
    Used: Method is used to get all users.
    """,
)
@inject
async def get_users(
    user_service: UserService = Depends(Provide[Services.v1.user_service]),
) -> list[models.User]:
    return await user_service.get_users()
