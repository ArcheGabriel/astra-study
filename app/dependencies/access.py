from fastapi import Depends
from sqlalchemy.orm import Session

from app.database.session import get_db
from app.dependencies.auth import get_current_user
from app.models.user import User
from app.repositories.org_manager_team import OrgManagerTeamRepository
from app.repositories.team_membership import TeamMembershipRepository
from app.retrieval.access import AccessContext


def get_access_context(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> AccessContext:
    """
    Build the request-scoped authorization identity.

    Every field is derived exclusively from server-side authenticated state:
    ``current_user`` (itself resolved from the validated JWT by
    ``get_current_user`` -- never from anything the client can set directly),
    this user's team memberships, and this user's Org Manager jurisdiction
    (RBAC-5J) -- both looked up fresh here. No request body, query
    parameter, or header beyond the bearer token feeds into this function.

    Team-membership and jurisdiction lookup failures are never swallowed:
    this function has no try/except, so a database error propagates
    unchanged rather than silently producing an incomplete or overly broad
    AccessContext.
    """

    team_membership_repository = TeamMembershipRepository(db)

    team_ids = team_membership_repository.get_team_ids_by_user_id(
        current_user.id,
    )

    org_manager_team_repository = OrgManagerTeamRepository(db)

    jurisdiction_team_ids = org_manager_team_repository.get_team_ids_by_user_id(
        current_user.id,
    )

    return AccessContext(
        user_id=current_user.id,
        organisation_id=current_user.organisation_id,
        team_ids=tuple(team_ids),
        jurisdiction_team_ids=tuple(jurisdiction_team_ids),
        role=current_user.role,
    )
