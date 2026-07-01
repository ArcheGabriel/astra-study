from app.core.security import security
from app.exceptions.auth import (
    InactiveUserError,
    InvalidCredentialsError,
)
from app.repositories.user import UserRepository
from app.schemas.auth import (
    LoginRequest,
    TokenResponse,
)
from app.schemas.user import UserResponse


class AuthService:
    """
    Handles authentication-related business logic.
    """

    def __init__(
        self,
        user_repository: UserRepository,
    ) -> None:
        self.user_repository = user_repository

    def authenticate(
        self,
        login_data: LoginRequest,
    ) -> TokenResponse:
        """
        Authenticate a user and return JWT tokens.
        """

        user = self.user_repository.get_by_email(
            login_data.email,
        )

        if user is None:
            raise InvalidCredentialsError()

        if not security.verify_password(
            login_data.password,
            user.hashed_password,
        ):
            raise InvalidCredentialsError()

        if not user.is_active:
            raise InactiveUserError()

        access_token = security.create_access_token(
            user_id=user.id,
        )

        refresh_token = security.create_refresh_token(
            user_id=user.id,
        )

        return TokenResponse(
            access_token=access_token,
            refresh_token=refresh_token,
            token_type="Bearer",
            user=UserResponse.model_validate(user),
        )