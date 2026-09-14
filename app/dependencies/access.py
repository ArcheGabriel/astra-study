from fastapi import Depends
from sqlalchemy.orm import Session

from app.database.session import get_db
from app.dependencies.auth import get_current_user
from app.models.user import User
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
    ``get_current_user`` -- never from anything the client can set directly)
    and this user's team memberships, looked up here. No request body, query
    parameter, or header beyond the bearer token feeds into this function.

    Team-membership lookup failures are never swallowed: this function has
    no try/except, so a database error propagates unchanged rather than
    silently producing an incomplete or overly broad AccessContext.
    """

    team_membership_repository = TeamMembershipRepository(db)

    team_ids = team_membership_repository.get_team_ids_by_user_id(
        current_user.id,
    )

    return AccessContext(
        user_id=current_user.id,
        organisation_id=current_user.organisation_id,
        team_ids=tuple(team_ids),
        role=current_user.role,
    )
