from fastapi import APIRouter, Depends, Response, status

from app.dependencies.access import get_access_context
from app.dependencies.services import (
    get_org_manager_team_service,
    get_team_membership_service,
    get_team_service,
)
from app.retrieval.access import AccessContext
from app.schemas.team import (
    AddTeamMemberRequest,
    OrgManagerTeamResponse,
    TeamCreate,
    TeamMemberResponse,
    TeamResponse,
    TeamRosterMemberResponse,
)
from app.services.org_manager_team import OrgManagerTeamService
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


@router.get(
    "/{team_id}/members",
    response_model=list[TeamRosterMemberResponse],
)
def get_team_members(
    team_id: int,
    access: AccessContext = Depends(get_access_context),
    team_membership_service: TeamMembershipService = Depends(
        get_team_membership_service,
    ),
) -> list[TeamRosterMemberResponse]:
    """
    Return every member of a team, ordered by username ascending.

    Only that team's own ``TeamRole.MANAGER`` may call this -- the same
    authorization boundary as add/remove/promote below, since the
    roster exists to support those same membership-management
    decisions, not general browsing.
    """

    return team_membership_service.list_members(
        access=access,
        team_id=team_id,
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


@router.get(
    "/{team_id}/managers",
    response_model=list[OrgManagerTeamResponse],
)
def get_team_managers(
    team_id: int,
    access: AccessContext = Depends(get_access_context),
    org_manager_team_service: OrgManagerTeamService = Depends(
        get_org_manager_team_service,
    ),
) -> list[OrgManagerTeamResponse]:
    """
    Return every Org Manager jurisdiction assignment for a team.

    Any authenticated user in the team's own organisation may call this
    -- a read of ``org_manager_teams`` only, requiring no
    ``TeamMembership`` and granting no new permission. A
    cross-organisation or nonexistent ``team_id`` raises the same
    enumeration-safe ``TeamNotFoundError`` (404) as grant/revoke below.
    """

    return org_manager_team_service.list_jurisdiction(
        access=access,
        team_id=team_id,
    )


@router.post(
    "/{team_id}/managers/{user_id}",
    response_model=OrgManagerTeamResponse,
    status_code=status.HTTP_201_CREATED,
)
def grant_org_manager_jurisdiction(
    team_id: int,
    user_id: int,
    access: AccessContext = Depends(get_access_context),
    org_manager_team_service: OrgManagerTeamService = Depends(
        get_org_manager_team_service,
    ),
) -> OrgManagerTeamResponse:
    """
    Grant an Org Manager jurisdiction over a team.

    Only ``OrgRole.ADMIN`` may call this. The target user must currently
    hold ``OrgRole.MANAGER`` in the ADMIN's own organisation.
    """

    return org_manager_team_service.grant_jurisdiction(
        access=access,
        team_id=team_id,
        user_id=user_id,
    )


@router.delete(
    "/{team_id}/managers/{user_id}",
    status_code=status.HTTP_204_NO_CONTENT,
)
def revoke_org_manager_jurisdiction(
    team_id: int,
    user_id: int,
    access: AccessContext = Depends(get_access_context),
    org_manager_team_service: OrgManagerTeamService = Depends(
        get_org_manager_team_service,
    ),
) -> Response:
    """
    Revoke an Org Manager's jurisdiction over a team.

    Only ``OrgRole.ADMIN`` may call this.
    """

    org_manager_team_service.revoke_jurisdiction(
        access=access,
        team_id=team_id,
        user_id=user_id,
    )

    return Response(
        status_code=status.HTTP_204_NO_CONTENT,
    )
