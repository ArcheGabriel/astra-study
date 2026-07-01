import jwt
from fastapi import Depends
from fastapi.security import OAuth2PasswordBearer

from app.core.security import security
from app.database.session import get_db
from app.exceptions.auth import AuthenticationError
from app.models.user import User
from app.repositories.user import UserRepository
from sqlalchemy.orm import Session

oauth2_scheme = OAuth2PasswordBearer(
    tokenUrl="/api/v1/auth/login",
)


def get_current_user(
    token: str = Depends(oauth2_scheme),
    db: Session = Depends(get_db),
) -> User:
    """
    Return the currently authenticated user.
    """

    try:
        payload = security.decode_token(token)

    except jwt.PyJWTError as exc:
        raise AuthenticationError() from exc

    token_type = payload.get("type")

    if token_type != "access":
        raise AuthenticationError()

    user_id = payload.get("sub")

    if user_id is None:
        raise AuthenticationError()

    user_repository = UserRepository(db)

    user = user_repository.get_by_id(
        int(user_id),
    )

    if user is None:
        raise AuthenticationError()

    return user