from app.exceptions.user import UsernameAlreadyExistsError
from app.exceptions.user import EmailAlreadyExistsError
from sqlalchemy.orm import Session

from app.models.user import User
from app.repositories.user import UserRepository
from app.schemas.user import UserCreate
from app.core.security import security


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

        user = User(
            username=user_data.username,
            email=user_data.email,
            hashed_password=hashed_password,
        )

        return self.user_repository.create(user)