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
