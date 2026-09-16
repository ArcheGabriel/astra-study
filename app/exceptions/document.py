from fastapi import status

from app.exceptions.base import AppException


class InvalidDocumentTypeError(AppException):
    """
    Raised when an unsupported file type is uploaded.
    """

    status_code = status.HTTP_400_BAD_REQUEST

    detail = (
        "Unsupported document type. "
        "Supported types are PDF, DOCX, PPTX, TXT, Markdown, PNG and JPEG."
    )


class EmptyDocumentError(AppException):
    """
    Raised when an empty document is uploaded.
    """

    status_code = status.HTTP_400_BAD_REQUEST

    detail = "Uploaded document is empty."


class DocumentTooLargeError(AppException):
    """
    Raised when a document exceeds the allowed size.
    """

    status_code = status.HTTP_413_CONTENT_TOO_LARGE

    detail = "Uploaded document exceeds the maximum allowed size."


class DocumentNotFoundError(AppException):
    """
    Raised when a requested document does not exist
    or does not belong to the current user.
    """

    status_code = status.HTTP_404_NOT_FOUND

    detail = "Document not found."


class InvalidAccessScopeError(AppException):
    """
    Raised for a malformed or self-contradictory scope/team_id
    combination on document creation -- an unrecognised ``access_scope``
    value, ``team_id`` supplied alongside INDIVIDUAL/ORGANISATION, or
    TEAM requested with no ``team_id``. A client input-shape problem,
    never an authorization decision.
    """

    status_code = status.HTTP_400_BAD_REQUEST

    detail = "Invalid document access scope or team selection."


class TeamNotFoundError(AppException):
    """
    Raised when the requested ``team_id`` does not exist, or exists in a
    different organisation than the requester's.

    Deliberately used for both cases -- exactly like
    ``DocumentNotFoundError`` collapsing "does not exist" and "not
    yours" into one response -- so a requester can never distinguish
    "no such team" from "that team belongs to another organisation" and
    enumerate other organisations' teams.
    """

    status_code = status.HTTP_404_NOT_FOUND

    detail = "Team not found."


class TeamMembershipRequiredError(AppException):
    """
    Raised when the requester is authenticated and the team exists in
    their own organisation, but they are not a member of it. Distinct
    from ``TeamNotFoundError``: the team's existence/organisation is
    already confirmed by this point, so there is no cross-organisation
    enumeration risk in stating the real reason.
    """

    status_code = status.HTTP_403_FORBIDDEN

    detail = "You are not a member of this team."


class OrganisationScopeForbiddenError(AppException):
    """
    Raised when a non-ADMIN requests ORGANISATION-scoped document
    creation.
    """

    status_code = status.HTTP_403_FORBIDDEN

    detail = "Only an organisation administrator may create an organisation-wide document."