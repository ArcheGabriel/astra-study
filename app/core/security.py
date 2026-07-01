from datetime import UTC, datetime, timedelta
from typing import Any

import jwt
from pwdlib import PasswordHash

from app.config.settings import settings


class SecurityManager:
    """
    Handles password hashing, password verification,
    and JWT token generation.
    """

    def __init__(self) -> None:
        self._password_hasher = PasswordHash.recommended()

    # ------------------------------------------------------------------
    # Password Hashing
    # ------------------------------------------------------------------

    def hash_password(
        self,
        password: str,
    ) -> str:
        """
        Hash a plain-text password.
        """

        return self._password_hasher.hash(password)

    def verify_password(
        self,
        plain_password: str,
        hashed_password: str,
    ) -> bool:
        """
        Verify a password against its hash.
        """

        return self._password_hasher.verify(
            plain_password,
            hashed_password,
        )

    # ------------------------------------------------------------------
    # JWT
    # ------------------------------------------------------------------

    def _create_token(
        self,
        *,
        user_id: int,
        token_type: str,
        expires_delta: timedelta,
    ) -> str:
        """
        Create a JWT.
        """

        now = datetime.now(UTC)

        payload = {
            "sub": str(user_id),
            "type": token_type,
            "iat": now,
            "exp": now + expires_delta,
        }

        return jwt.encode(
            payload,
            settings.JWT_SECRET_KEY,
            algorithm=settings.JWT_ALGORITHM,
        )

    def create_access_token(
        self,
        user_id: int,
    ) -> str:
        """
        Create an access token.
        """

        return self._create_token(
            user_id=user_id,
            token_type="access",
            expires_delta=timedelta(
                minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES,
            ),
        )

    def create_refresh_token(
        self,
        user_id: int,
    ) -> str:
        """
        Create a refresh token.
        """

        return self._create_token(
            user_id=user_id,
            token_type="refresh",
            expires_delta=timedelta(
                days=settings.REFRESH_TOKEN_EXPIRE_DAYS,
            ),
        )

    def decode_token(
        self,
        token: str,
    ) -> dict[str, Any]:
        """
        Decode and validate a JWT.
        """

        return jwt.decode(
            token,
            settings.JWT_SECRET_KEY,
            algorithms=[settings.JWT_ALGORITHM],
        )


security = SecurityManager()