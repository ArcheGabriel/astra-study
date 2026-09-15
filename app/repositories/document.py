from sqlalchemy import and_, or_, select
from sqlalchemy.orm import Session

from app.enums.document import DocumentAccessScope, DocumentStatus
from app.enums.organisation import OrgRole
from app.models.document import Document
from app.repositories.base import BaseRepository
from app.retrieval.access import AccessContext


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

    @staticmethod
    def _visibility_conditions(
        access: AccessContext,
    ) -> list:
        """
        The SQL-level mirror of ``DenseRepository._authorization_filter``'s
        branch logic: individual (own), team (member, same organisation),
        organisation (ADMIN only, same organisation). Kept in one place so
        list/get/download can never authorize inconsistently with one
        another -- see ``get_visible`` / ``get_by_id_visible``.

        This does not change, and is not used by, the Qdrant retrieval
        filter itself -- it is the equivalent decision applied to the
        relational ``documents`` table for the document-management API.
        """

        conditions = [
            and_(
                Document.access_scope == DocumentAccessScope.INDIVIDUAL,
                Document.user_id == access.user_id,
            ),
        ]

        if access.team_ids:
            conditions.append(
                and_(
                    Document.access_scope == DocumentAccessScope.TEAM,
                    Document.organisation_id == access.organisation_id,
                    Document.team_id.in_(access.team_ids),
                ),
            )

        if access.role == OrgRole.ADMIN:
            conditions.append(
                and_(
                    Document.access_scope == DocumentAccessScope.ORGANISATION,
                    Document.organisation_id == access.organisation_id,
                ),
            )

        return conditions

    def get_visible(
        self,
        access: AccessContext,
    ) -> list[Document]:
        """
        Return every document ``access`` is authorized to see: owned
        INDIVIDUAL documents, TEAM documents for a team in
        ``access.team_ids`` (same organisation), and -- ADMIN only --
        ORGANISATION documents in ``access.organisation_id``.
        """

        statement = (
            select(Document)
            .where(or_(*self._visibility_conditions(access)))
            .order_by(Document.created_at.desc())
        )

        result = self.db.execute(
            statement,
        )

        return list(
            result.scalars().all(),
        )

    def get_by_id_visible(
        self,
        *,
        document_id: int,
        access: AccessContext,
    ) -> Document | None:
        """
        Return one document only if ``access`` is authorized to see it --
        same visibility rules as ``get_visible``, scoped to a single id.
        """

        statement = (
            select(Document)
            .where(Document.id == document_id)
            .where(or_(*self._visibility_conditions(access)))
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