from fastapi import APIRouter, Depends, Response, status

from app.dependencies.access import get_access_context
from app.dependencies.services import get_team_membership_service, get_team_service
from app.retrieval.access import AccessContext
from app.schemas.team import (
    AddTeamMemberRequest,
    TeamCreate,
    TeamMemberResponse,
    TeamResponse,
)
from app.services.team import TeamService
from app.services.team_membership import TeamMembershipService

router = APIRouter(
    prefix="/teams",
    tags=["Teams"],
)


@router.post(
    "",
    response_model=TeamResponse,
    status_code=status.HTTP_201_CREATED,
)
def create_team(
    team_data: TeamCreate,
    access: AccessContext = Depends(get_access_context),
    team_service: TeamService = Depends(get_team_service),
) -> TeamResponse:
    """
    Create a team in the requester's own organisation. Requires
    ``OrgRole.ADMIN`` or ``OrgRole.MANAGER``; the requester becomes the
    team's sole initial ``TeamRole.MANAGER``.
    """

    return team_service.create_team(
        access=access,
        name=team_data.name,
    )


@router.get(
    "",
    response_model=list[TeamResponse],
)
def list_teams(
    access: AccessContext = Depends(get_access_context),
    team_service: TeamService = Depends(get_team_service),
) -> list[TeamResponse]:
    """
    Return every team in the requester's own organisation. Membership is
    never required to appear in this list.
    """

    return team_service.list_teams(
        access=access,
    )


@router.post(
    "/{team_id}/members",
    response_model=TeamMemberResponse,
    status_code=status.HTTP_201_CREATED,
)
def add_team_member(
    team_id: int,
    member_data: AddTeamMemberRequest,
    access: AccessContext = Depends(get_access_context),
    team_membership_service: TeamMembershipService = Depends(
        get_team_membership_service,
    ),
) -> TeamMemberResponse:
    """
    Add an existing user to a team as a plain ``TeamRole.MEMBER``.

    Only that team's own ``TeamRole.MANAGER`` may call this.
    """

    return team_membership_service.add_member(
        access=access,
        team_id=team_id,
        user_id=member_data.user_id,
    )


@router.delete(
    "/{team_id}/members/{user_id}",
    status_code=status.HTTP_204_NO_CONTENT,
)
def remove_team_member(
    team_id: int,
    user_id: int,
    access: AccessContext = Depends(get_access_context),
    team_membership_service: TeamMembershipService = Depends(
        get_team_membership_service,
    ),
) -> Response:
    """
    Remove a user's membership from a team entirely, regardless of its
    current role.

    Only that team's own ``TeamRole.MANAGER`` may call this. Removing a
    ``TeamRole.MANAGER`` is rejected unless another manager remains on
    the team afterward -- a team must always retain at least one
    manager. This is never a demotion.
    """

    team_membership_service.remove_member(
        access=access,
        team_id=team_id,
        user_id=user_id,
    )

    return Response(
        status_code=status.HTTP_204_NO_CONTENT,
    )


@router.post(
    "/{team_id}/members/{user_id}/promote",
    response_model=TeamMemberResponse,
)
def promote_team_member(
    team_id: int,
    user_id: int,
    access: AccessContext = Depends(get_access_context),
    team_membership_service: TeamMembershipService = Depends(
        get_team_membership_service,
    ),
) -> TeamMemberResponse:
    """
    Promote an existing ``TeamRole.MEMBER`` to ``TeamRole.MANAGER``.

    Only that team's own ``TeamRole.MANAGER`` may call this. There is
    no reverse (``MANAGER -> MEMBER`` demotion) operation.
    """

    return team_membership_service.promote_member(
        access=access,
        team_id=team_id,
        user_id=user_id,
    )
