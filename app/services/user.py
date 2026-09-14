from sqlalchemy import select

from app.exceptions.user import UsernameAlreadyExistsError
from app.exceptions.user import EmailAlreadyExistsError

from app.models.organisation import Organisation
from app.models.user import User
from app.repositories.user import UserRepository
from app.schemas.user import UserCreate
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
    ):
        self.user_repository = user_repository

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