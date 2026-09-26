from starlette import status

from app.exceptions.base import AppException


class TeamCreationForbiddenError(AppException):
    """
    Raised when a non-ADMIN, non-MANAGER user attempts to create a team.
    """

    status_code = status.HTTP_403_FORBIDDEN

    detail = "Only an organisation administrator or manager may create a team."


class TeamNameAlreadyExistsError(AppException):
    """
    Raised when a team name is already taken within the requester's
    organisation. The same name remains free to use in a different
    organisation -- uniqueness is scoped to (organisation_id, name).
    """

    status_code = status.HTTP_409_CONFLICT

    detail = "A team with this name already exists in your organisation."


class InvalidTeamNameError(AppException):
    """
    Raised when a team name is blank/whitespace-only after trimming, or
    exceeds 255 characters. A client input-shape problem, never an
    authorization decision -- mirrors
    ``app.exceptions.document.InvalidAccessScopeError``'s role for
    malformed document-creation input. ``TeamCreate`` already rejects
    these at the schema layer; this exists so ``TeamService.create_team``
    enforces the identical invariant independently of that schema, for
    any caller that invokes it directly.
    """

    status_code = status.HTTP_400_BAD_REQUEST

    detail = "Team name must be between 1 and 255 characters after trimming whitespace."


class TeamMembershipOperationForbiddenError(AppException):
    """
    Raised when the acting user is not the target team's own
    ``TeamRole.MANAGER``. Distinct from
    ``app.exceptions.document.TeamMembershipRequiredError`` (which means
    "not a member of this team at all," the bar for TEAM document
    creation) -- this means "a member, or not, but not that specific
    team's manager," the bar for direct membership management
    (RBAC-5I). ``OrgRole.ADMIN`` and ``OrgRole.MANAGER`` alone (without
    being that team's ``TeamRole.MANAGER``) both raise this too --
    neither role bypasses per-team manager authorization here.
    """

    status_code = status.HTTP_403_FORBIDDEN

    detail = "Only that team's manager may manage its membership."


class TeamMemberNotFoundError(AppException):
    """
    Raised when the target user has no ``TeamMembership`` row for the
    given team -- covers removing or promoting a non-member.
    """

    status_code = status.HTTP_404_NOT_FOUND

    detail = "User is not a member of this team."


class TeamMembershipAlreadyExistsError(AppException):
    """
    Raised when adding a user who is already a member of the team, or
    promoting a user who already holds ``TeamRole.MANAGER`` on it --
    both are "this membership state already exists" conditions.
    """

    status_code = status.HTTP_409_CONFLICT

    detail = "This team membership already exists."


class LastTeamManagerError(AppException):
    """
    Raised when removing a ``TeamRole.MANAGER`` would leave the team
    with zero managers. A team must always retain at least one manager
    -- the only way a manager stops being one is by being removed from
    the team entirely, and only when another manager remains to take
    over (see RBAC-5I's frozen team-role lifecycle: there is no
    MANAGER -> MEMBER demotion).
    """

    status_code = status.HTTP_409_CONFLICT

    detail = "Cannot remove the team's last remaining manager."
