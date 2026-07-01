from pydantic import BaseModel, EmailStr, Field

from app.schemas.user import UserResponse


class LoginRequest(BaseModel):
    """
    Request schema for user login.
    """

    email: EmailStr = Field(
        ...,
        description="Registered email address.",
        examples=["rupam@example.com"],
    )

    password: str = Field(
        ...,
        min_length=8,
        description="User password.",
        examples=["Password@123"],
    )


class TokenResponse(BaseModel):
    """
    Response returned after successful authentication.
    """

    access_token: str = Field(
        ...,
        description="JWT access token.",
    )

    refresh_token: str = Field(
        ...,
        description="JWT refresh token.",
    )

    token_type: str = Field(
        default="Bearer",
        description="Authentication scheme.",
    )

    user: UserResponse


class RefreshTokenRequest(BaseModel):
    """
    Request schema for refreshing an access token.
    """

    refresh_token: str = Field(
        ...,
        description="Refresh token issued during login.",
    )


class RefreshTokenResponse(BaseModel):
    """
    Response returned after refreshing an access token.
    """

    access_token: str = Field(
        ...,
        description="New JWT access token.",
    )

    token_type: str = Field(
        default="Bearer",
        description="Authentication scheme.",
    )