from sqlalchemy import or_, select
from sqlalchemy.orm import Session

from app.models.user import User
from app.repositories.base import BaseRepository


class UserRepository(BaseRepository[User]):
    """
    Repository for User-specific database operations.
    """

    def __init__(self, db: Session):
        super().__init__(db=db, model=User)

    def get_by_email(
        self,
        email: str,
    ) -> User | None:
        """
        Retrieve a user by email.
        """

        statement = select(User).where(
            User.email == email
        )

        result = self.db.execute(statement)

        return result.scalar_one_or_none()

    def search_by_organisation(
        self,
        *,
        organisation_id: int,
        query: str,
        limit: int,
    ) -> list[User]:
        """
        Search for users within one organisation by a case-insensitive
        partial match on username or email.

        Organisation-scoped so a user in one organisation can never be
        discovered by a search from another -- the caller must always
        pass the requester's own ``organisation_id`` (from the trusted
        ``AccessContext``), never a client-supplied value. Ordered by
        username ascending and capped at ``limit`` results for a
        deterministic, bounded response -- this is a lookup to identify
        one user for team membership management, not a general-purpose
        directory listing.
        """

        pattern = f"%{query}%"

        statement = (
            select(User)
            .where(
                User.organisation_id == organisation_id,
                or_(
                    User.username.ilike(pattern),
                    User.email.ilike(pattern),
                ),
            )
            .order_by(User.username)
            .limit(limit)
        )

        result = self.db.execute(statement)

        return list(result.scalars().all())

    def get_by_username(
        self,
        username: str,
    ) -> User | None:
        """
        Retrieve a user by username.
        """

        statement = select(User).where(
            User.username == username
        )

        result = self.db.execute(statement)

        return result.scalar_one_or_none()