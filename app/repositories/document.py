from sqlalchemy import select
from sqlalchemy.orm import Session

from app.enums.document import DocumentStatus
from app.models.document import Document
from app.repositories.base import BaseRepository


class DocumentRepository(BaseRepository[Document]):
    """
    Repository for Document database operations.
    """

    def __init__(
        self,
        db: Session,
    ) -> None:
        super().__init__(
            db=db,
            model=Document,
        )

    def get_by_user(
        self,
        user_id: int,
    ) -> list[Document]:
        """
        Return all documents belonging to a user.
        """

        statement = (
            select(Document)
            .where(Document.user_id == user_id)
            .order_by(Document.created_at.desc())
        )

        result = self.db.execute(
            statement,
        )

        return list(
            result.scalars().all(),
        )

    def get_by_id_and_user(
        self,
        *,
        document_id: int,
        user_id: int,
    ) -> Document | None:
        """
        Return a document only if it belongs to the specified user.
        """

        statement = (
            select(Document)
            .where(Document.id == document_id)
            .where(Document.user_id == user_id)
        )

        result = self.db.execute(
            statement,
        )

        return result.scalar_one_or_none()

    def update_status(
        self,
        *,
        document_id: int,
        status: DocumentStatus,
    ) -> Document | None:
        """
        Update the processing status of a document.
        """

        document = self.get_by_id(
            document_id,
        )

        if document is None:
            return None

        document.status = status

        self.db.commit()

        self.db.refresh(
            document,
        )

        return document