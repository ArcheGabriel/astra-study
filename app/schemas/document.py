from datetime import datetime

from pydantic import BaseModel, ConfigDict

from app.enums.document import DocumentStatus


class DocumentResponse(BaseModel):
    """
    Response returned for uploaded documents.
    """

    id: int

    filename: str

    content_type: str

    file_size: int

    status: DocumentStatus

    created_at: datetime

    model_config = ConfigDict(
        from_attributes=True,
    )