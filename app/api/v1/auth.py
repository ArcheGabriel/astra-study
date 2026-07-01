from fastapi import APIRouter, Depends, status

from app.dependencies.services import (
    get_auth_service,
    get_user_service,
)
from app.schemas.auth import (
    LoginRequest,
    TokenResponse,
)
from app.schemas.user import (
    UserCreate,
    UserResponse,
)
from app.services.auth import AuthService
from app.services.user import UserService

router = APIRouter(
    prefix="/auth",
    tags=["Authentication"],
)


@router.post(
    "/register",
    response_model=UserResponse,
    status_code=status.HTTP_201_CREATED,
)
def register(
    user_data: UserCreate,
    user_service: UserService = Depends(get_user_service),
) -> UserResponse:
    """
    Register a new user.
    """

    user = user_service.register(user_data)

    return UserResponse.model_validate(user)


@router.post(
    "/login",
    response_model=TokenResponse,
    status_code=status.HTTP_200_OK,
)
def login(
    login_data: LoginRequest,
    auth_service: AuthService = Depends(get_auth_service),
) -> TokenResponse:
    """
    Authenticate a user and return JWT tokens.
    """

    return auth_service.authenticate(login_data)