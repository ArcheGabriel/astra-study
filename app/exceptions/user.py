from starlette import status

from app.exceptions.base import AppException


class EmailAlreadyExistsError(AppException):
    """
    Raised when an email is already registered.
    """

    status_code = status.HTTP_409_CONFLICT

    detail = "Email is already registered."


class UsernameAlreadyExistsError(AppException):
    """
    Raised when a username is already taken.
    """

    status_code = status.HTTP_409_CONFLICT

    detail = "Username is already taken."


class UserNotFoundError(AppException):
    """
    Raised when a target user id does not exist, or belongs to a
    different organisation than the requester's -- both cases collapse
    into the same response, mirroring
    ``app.exceptions.document.TeamNotFoundError``'s enumeration-safety
    precedent for cross-organisation team ids: a requester can never
    distinguish "no such user" from "that user belongs to another
    organisation."
    """

    status_code = status.HTTP_404_NOT_FOUND

    detail = "User not found."


class RoleAdministrationForbiddenError(AppException):
    """
    Raised when a non-``OrgRole.ADMIN`` attempts to change another user's
    ``OrgRole`` (RBAC Phase C.2). Mirrors
    ``app.exceptions.team.OrgManagerJurisdictionForbiddenError``'s exact
    shape for the analogous ADMIN-only action -- kept as its own
    exception (rather than reusing that one) since its detail text is
    specific to role administration, not jurisdiction.
    """

    status_code = status.HTTP_403_FORBIDDEN

    detail = "Only an organisation administrator may change another user's role."


class SelfRoleModificationForbiddenError(AppException):
    """
    Raised when a caller attempts to change their own ``OrgRole``,
    regardless of their current role. Checked immediately after ADMIN
    authorization and before any target-user resolution, so it never
    depends on -- or leaks information via -- a database read.
    """

    status_code = status.HTTP_403_FORBIDDEN

    detail = "Users cannot modify their own organisation role."


class InvalidRoleTransitionError(AppException):
    """
    Raised when the requested ``(current_role, target_role)`` pair is not
    one of the two explicitly allowed transitions
    (``MEMBER -> MANAGER``, ``MANAGER -> ADMIN``). A client-input-shape
    problem given the target's current state, not a question of the
    caller's authority -- mirrors
    ``app.exceptions.team.TargetNotOrgManagerError``'s precedent for the
    same distinction (400, not 403). This is also what structurally
    prevents any downward transition or an existing ADMIN's role from
    ever changing: ``(OrgRole.ADMIN, *)`` never appears in the allowed
    set, so an ADMIN can never be demoted through this endpoint.
    """

    status_code = status.HTTP_400_BAD_REQUEST

    detail = "The requested role transition is not permitted."
