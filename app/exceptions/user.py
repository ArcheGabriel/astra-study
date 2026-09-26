from starlette import status

from app.exceptions.base import AppException


class EmailAlreadyExistsError(AppException):
    """
    Raised when an email is already registered.
    """

    status_code = status.HTTP_409_CONFLICT

    detail = "Email is already registered."


class UsernameAlreadyExistsError(AppException):
    """
    Raised when a username is already taken.
    """

    status_code = status.HTTP_409_CONFLICT

    detail = "Username is already taken."


class UserNotFoundError(AppException):
    """
    Raised when a target user id does not exist, or belongs to a
    different organisation than the requester's -- both cases collapse
    into the same response, mirroring
    ``app.exceptions.document.TeamNotFoundError``'s enumeration-safety
    precedent for cross-organisation team ids: a requester can never
    distinguish "no such user" from "that user belongs to another
    organisation."
    """

    status_code = status.HTTP_404_NOT_FOUND

    detail = "User not found."