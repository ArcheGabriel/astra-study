from pydantic import BaseModel, ConfigDict, EmailStr, Field


class UserCreate(BaseModel):
    """
    Schema used when a new user registers.
    """

    username: str = Field(
        min_length=3,
        max_length=50,
    )

    email: EmailStr

    password: str = Field(
        min_length=8,
        max_length=128,
    )

    model_config = ConfigDict(
        extra="forbid",
    )


class UserResponse(BaseModel):
    """
    Schema returned after a successful registration.
    """

    id: int
    username: str
    email: EmailStr

    model_config = ConfigDict(
        from_attributes=True,
        extra="forbid",
    )