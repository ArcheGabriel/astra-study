from sqlalchemy import select

from app.exceptions.user import UsernameAlreadyExistsError
from app.exceptions.user import EmailAlreadyExistsError

from app.models.organisation import Organisation
from app.models.user import User
from app.repositories.org_manager_team import OrgManagerTeamRepository
from app.repositories.team_membership import TeamMembershipRepository
from app.repositories.user import UserRepository
from app.schemas.user import (
    ManagedTeamResponse,
    TeamMembershipResponse,
    UserCreate,
    UserProfileResponse,
)
from app.core.security import security

# Every newly registered user is attached to the single organisation seeded
# by the RBAC foundation migration (see
# alembic/versions/116ced32c143_rbac_organisation_team_foundation.py). This
# is not a client-selectable value -- registration must never let a caller
# choose an organisation or a role (UserCreate has extra="forbid" and no
# role field; new users always default to OrgRole.MEMBER on the model).
DEFAULT_ORGANISATION_SLUG = "default"


class UserService:
    """
    Service responsible for user-related business logic.
    """

    def __init__(
        self,
        user_repository: UserRepository,
        team_membership_repository: TeamMembershipRepository,
        org_manager_team_repository: OrgManagerTeamRepository,
    ):
        self.user_repository = user_repository
        self.team_membership_repository = team_membership_repository
        self.org_manager_team_repository = org_manager_team_repository

    def register(
        self,
        user_data: UserCreate,
    ) -> User:
        """
        Register a new user.

        Every new user is attached to the seeded default organisation as
        OrgRole.MEMBER (the model default) -- registration never accepts an
        organisation or a role from the client.
        """

        existing_user = self.user_repository.get_by_email(
            user_data.email
        )

        if existing_user:
            raise EmailAlreadyExistsError()

        existing_user = self.user_repository.get_by_username(
            user_data.username
        )

        if existing_user:
            raise UsernameAlreadyExistsError()

        hashed_password = security.hash_password(
            user_data.password
        )

        organisation = self._get_default_organisation()

        user = User(
            username=user_data.username,
            email=user_data.email,
            hashed_password=hashed_password,
            organisation_id=organisation.id,
        )

        return self.user_repository.create(user)

    def _get_default_organisation(self) -> Organisation:
        """
        Resolve the seeded default organisation by its stable slug.

        Looked up by slug (never a hardcoded id) so this stays correct
        regardless of insertion order. Fails loudly rather than silently
        creating a second "default" organisation -- an empty result means
        the RBAC foundation migration has not been applied, which is a
        deployment error to surface immediately, not paper over.
        """

        statement = select(Organisation).where(
            Organisation.slug == DEFAULT_ORGANISATION_SLUG
        )

        organisation = self.user_repository.db.execute(
            statement
        ).scalar_one_or_none()

        if organisation is None:
            raise RuntimeError(
                "Default organisation "
                f"(slug={DEFAULT_ORGANISATION_SLUG!r}) not found. "
                "Has the RBAC foundation migration been applied?"
            )

        return organisation

    def get_profile(
        self,
        user: User,
    ) -> UserProfileResponse:
        """
        Build the ``GET /users/me`` response for an already-authenticated
        user.

        ``organisation_id``/``role`` come directly from ``user`` (already
        loaded, no extra query); team memberships come from a single
        eager-loaded repository query, and Org Manager jurisdiction
        (RBAC-5J) from a second, independent repository query -- kept
        structurally separate from ``teams``, never merged, since
        membership and jurisdiction are two different relationships (a
        user may appear in either, both, or neither). Never uses
        ``AccessContext`` -- that value object deliberately carries no
        team name/per-team ``TeamRole``, and ``organisation_id``/``role``
        are already on ``user`` -- so it would add a second, heavier
        identity-resolution path for values already in hand.
        """

        memberships = (
            self.team_membership_repository.get_memberships_with_team_by_user_id(
                user.id,
            )
        )

        jurisdictions = (
            self.org_manager_team_repository.get_jurisdictions_with_team_by_user_id(
                user.id,
            )
        )

        return UserProfileResponse(
            id=user.id,
            username=user.username,
            email=user.email,
            organisation_id=user.organisation_id,
            role=user.role,
            teams=[
                TeamMembershipResponse(
                    team_id=membership.team_id,
                    team_name=membership.team.name,
                    role=membership.role,
                )
                for membership in memberships
            ],
            managed_teams=[
                ManagedTeamResponse(
                    team_id=team_id,
                    team_name=team_name,
                )
                for team_id, team_name in jurisdictions
            ],
        )