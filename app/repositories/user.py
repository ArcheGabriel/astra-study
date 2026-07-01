from sqlalchemy import select
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