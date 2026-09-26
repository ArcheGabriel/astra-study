from fastapi import APIRouter, Depends, status

from app.dependencies.access import get_access_context
from app.dependencies.services import get_team_service
from app.retrieval.access import AccessContext
from app.schemas.team import TeamCreate, TeamResponse
from app.services.team import TeamService

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
