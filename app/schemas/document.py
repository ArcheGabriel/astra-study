from datetime import datetime

from pydantic import BaseModel, ConfigDict

from app.enums.document import DocumentAccessScope, DocumentStatus


class DocumentResponse(BaseModel):
    """
    Response returned for uploaded documents.

    ``access_scope``/``team_id``/``organisation_id`` (RBAC-8) are the
    document's existing RBAC metadata, already present on every
    ``Document`` row -- this is a read-only visibility exposure, not a
    new capability. ``team_id`` is genuinely ``None`` for INDIVIDUAL and
    ORGANISATION documents (see ``DocumentAccessScope``); never fabricated.
    """

    id: int

    filename: str

    content_type: str

    file_size: int

    status: DocumentStatus

    created_at: datetime

    access_scope: DocumentAccessScope

    team_id: int | None

    organisation_id: int

    model_config = ConfigDict(
        from_attributes=True,
    )