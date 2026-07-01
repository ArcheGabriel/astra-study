from typing import Annotated

from fastapi import Depends

from app.database.session import get_db
from app.repositories.user import UserRepository
from app.services.auth import AuthService
from app.services.user import UserService
from sqlalchemy.orm import Session


def get_user_service(
    db: Annotated[Session, Depends(get_db)],
) -> UserService:
    """
    Dependency for UserService.
    """

    user_repository = UserRepository(db)

    return UserService(
        user_repository=user_repository,
    )


def get_auth_service(
    db: Annotated[Session, Depends(get_db)],
) -> AuthService:
    """
    Dependency for AuthService.
    """

    user_repository = UserRepository(db)

    return AuthService(
        user_repository=user_repository,
    )