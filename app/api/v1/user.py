from fastapi import APIRouter, Depends, Query

from app.dependencies.access import get_access_context
from app.dependencies.auth import get_current_user
from app.dependencies.services import get_user_service
from app.models.user import User
from app.retrieval.access import AccessContext
from app.schemas.user import UserProfileResponse, UserResponse
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


@router.get(
    "",
    response_model=list[UserResponse],
)
def search_users(
    q: str = Query(
        ...,
        min_length=1,
        max_length=100,
    ),
    access: AccessContext = Depends(get_access_context),
    user_service: UserService = Depends(get_user_service),
) -> list[UserResponse]:
    """
    Search for users within the requester's own organisation by a
    partial, case-insensitive match on username or email.

    Scoped to ``access.organisation_id`` (the trusted, request-derived
    identity) -- a user in a different organisation can never appear in
    the result, and a client can never supply an organisation to search
    instead. Intended to resolve a ``user_id`` for team membership
    management, not as a general-purpose user directory: ``q`` is
    required (there is no "list every user" call shape) and results are
    capped (see ``UserService.search_organisation_users``).
    """

    return user_service.search_organisation_users(
        access=access,
        query=q,
    )
