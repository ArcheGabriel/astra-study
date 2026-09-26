from app.enums.organisation import OrgRole
from app.exceptions.team import (
    InvalidTeamNameError,
    TeamCreationForbiddenError,
    TeamNameAlreadyExistsError,
)
from app.models.team import Team
from app.repositories.team import TeamRepository
from app.retrieval.access import AccessContext
from app.schemas.team import TeamResponse


class TeamService:
    """
    Handles team creation and organisation-scoped team listing.

    Membership management, role promotion/demotion, rename, and delete
    are all explicitly out of scope for this stage -- see RBAC-5H's
    investigation and implementation-plan reports.
    """

    def __init__(
        self,
        team_repository: TeamRepository,
    ) -> None:
        self.team_repository = team_repository

    def create_team(
        self,
        *,
        access: AccessContext,
        name: str,
    ) -> TeamResponse:
        """
        Create a team in the requester's own organisation, with the
        requester installed as its sole initial ``TeamRole.MANAGER``.

        Authorization runs first, before any database read tied to the
        request body -- ``OrgRole.MEMBER`` is rejected before the
        duplicate-name lookup even runs. ``organisation_id`` is always
        ``access.organisation_id`` and the creator is always
        ``access.user_id`` -- neither is ever accepted from the request.

        ``name`` is trimmed and validated here too (not only by
        ``TeamCreate``'s own schema-level constraints), so this method
        enforces the same non-blank / max-255 invariant correctly for any
        caller, including tests that exercise it directly without going
        through the API/schema layer.
        """

        if access.role not in (OrgRole.ADMIN, OrgRole.MANAGER):
            raise TeamCreationForbiddenError()

        name = name.strip()

        if not name or len(name) > 255:
            raise InvalidTeamNameError()

        existing = self.team_repository.get_by_organisation_and_name(
            organisation_id=access.organisation_id,
            name=name,
        )

        if existing is not None:
            raise TeamNameAlreadyExistsError()

        team = self.team_repository.create_with_initial_manager(
            organisation_id=access.organisation_id,
            name=name,
            creator_user_id=access.user_id,
        )

        return TeamResponse.model_validate(team)

    def list_teams(
        self,
        *,
        access: AccessContext,
    ) -> list[TeamResponse]:
        """
        Return every team in the requester's own organisation, ordered
        by id ascending. Membership is never a filter -- appearing in
        this list does not imply the requester belongs to the team.
        """

        teams: list[Team] = self.team_repository.list_by_organisation(
            access.organisation_id,
        )

        return [
            TeamResponse.model_validate(team)
            for team in teams
        ]
