from enum import Enum


class DocumentStatus(
    str,
    Enum,
):
    """
    Processing state of a document.
    """

    UPLOADED = "uploaded"

    PROCESSING = "processing"

    INDEXED = "indexed"

    FAILED = "failed"


class DocumentAccessScope(
    str,
    Enum,
):
    """
    Who can retrieve/query a document.

    Separate from ``OrgRole`` / ``TeamRole`` -- access scope is a property
    of the document, never derived from the requester's role.
    """

    INDIVIDUAL = "individual"

    TEAM = "team"

    ORGANISATION = "organisation"