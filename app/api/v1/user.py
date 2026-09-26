from fastapi import APIRouter, Depends

from app.dependencies.auth import get_current_user
from app.dependencies.services import get_user_service
from app.models.user import User
from app.schemas.user import UserProfileResponse
from app.services.user import UserService

router = APIRouter(
    prefix="/users",
    tags=["Users"],
)


@router.get(
    "/me",
    response_model=UserProfileResponse,
)
def get_current_user_profile(
    current_user: User = Depends(get_current_user),
    user_service: UserService = Depends(get_user_service),
) -> UserProfileResponse:
    """
    Return the currently authenticated user's profile, including their
    organisation role and team memberships.
    """

    return user_service.get_profile(current_user)
