from pathlib import Path

from fastapi import UploadFile

from app.enums.document import DocumentAccessScope, DocumentStatus
from app.enums.organisation import OrgRole
from app.enums.team import TeamRole
from app.exceptions.document import DocumentNotFoundError
from app.models.document import Document
from app.models.user import User
from app.repositories.document import DocumentRepository
from app.repositories.team_membership import TeamMembershipRepository
from app.retrieval.access import AccessContext
from app.schemas.document import DocumentResponse
from app.search.dense.repository import DenseRepository
from app.storage.base import BaseStorageService
from app.validators.document import DocumentValidator


class DocumentService:
    """
    Handles document upload, read, and delete business logic.

    Read/delete authorization is based on the trusted ``AccessContext``
    (identity, role, organisation, team membership) -- never on
    ``document_id``/``team_id``/``organisation_id`` alone. Upload behavior
    is unchanged by this: every new document is still created as
    INDIVIDUAL-scoped, owned by the uploader (RBAC-5D intentionally does
    not add scope/team selection to upload -- see ``upload_documents``).
    """

    def __init__(
        self,
        document_repository: DocumentRepository,
        storage_service: BaseStorageService,
        team_membership_repository: TeamMembershipRepository,
        dense_repository: DenseRepository,
    ) -> None:
        self.document_repository = document_repository
        self.storage_service = storage_service
        self.team_membership_repository = team_membership_repository
        self.dense_repository = dense_repository

    async def upload_documents(
        self,
        *,
        files: list[UploadFile],
        current_user: User,
    ) -> list[Document]:
        """
        Upload one or more documents.

        Returns the created Document models.
        """

        uploaded_documents: list[Document] = []

        for file in files:

            await DocumentValidator.validate(
                file,
            )

            stored_filename, file_size = (
                await self.storage_service.save_file(
                    file,
                )
            )

            document = Document(
                user_id=current_user.id,
                organisation_id=current_user.organisation_id,
                filename=file.filename,
                stored_filename=stored_filename,
                content_type=file.content_type,
                file_size=file_size,
                status=DocumentStatus.UPLOADED,
            )

            created_document = (
                self.document_repository.create(
                    document,
                )
            )

            uploaded_documents.append(
                created_document,
            )

        return uploaded_documents

    def get_documents(
        self,
        *,
        access: AccessContext,
    ) -> list[DocumentResponse]:
        """
        Retrieve every document ``access`` is authorized to see:
        owned INDIVIDUAL documents, TEAM documents for a team the
        requester belongs to, and -- ADMIN only -- ORGANISATION
        documents in the requester's organisation.
        """

        documents = (
            self.document_repository.get_visible(
                access,
            )
        )

        return [
            DocumentResponse.model_validate(
                document,
            )
            for document in documents
        ]

    def get_document(
        self,
        *,
        document_id: int,
        access: AccessContext,
    ) -> DocumentResponse:
        """
        Retrieve a single document, if ``access`` is authorized to see it.

        Unauthorized and nonexistent documents are indistinguishable
        (``DocumentNotFoundError`` / 404 either way) -- no enumeration
        signal.
        """

        document = (
            self.document_repository.get_by_id_visible(
                document_id=document_id,
                access=access,
            )
        )

        if document is None:
            raise DocumentNotFoundError()

        return DocumentResponse.model_validate(
            document,
        )

    async def delete_document(
        self,
        *,
        document_id: int,
        access: AccessContext,
    ) -> None:
        """
        Delete a document, its Qdrant vectors, and its stored file --
        only if ``access`` is authorized to delete it.

        Authorization is resolved BEFORE any destructive operation, and
        never from ``document_id``/``team_id``/``organisation_id`` alone
        -- see ``_can_delete``.

        Ordering (deliberate, not a distributed transaction): Qdrant
        vectors are deleted first. If that fails, the exception
        propagates and nothing else is touched -- the document, its SQL
        row, and its stored file are left completely intact, so a failed
        deletion never leaves the previous bug's inconsistent state
        (SQL/file gone, Qdrant vectors orphaned and still retrievable
        forever). Only once Qdrant deletion has succeeded (or was
        correctly skipped for a legacy schema_version=2 document -- see
        ``DenseRepository.delete_by_document_id``) do the file and SQL
        row get removed. There is no rollback of the file/SQL steps if
        one of them fails after Qdrant deletion succeeds -- a fully
        atomic multi-system delete is out of scope for this stage; this
        ordering is the safest available without one.
        """

        document = self.document_repository.get_by_id(
            document_id,
        )

        if document is None or not self._can_delete(document, access):
            raise DocumentNotFoundError()

        self.dense_repository.delete_by_document_id(
            document.id,
        )

        await self.storage_service.delete_file(
            document.stored_filename,
        )

        self.document_repository.delete(
            document,
        )

    def download_document(
        self,
        *,
        document_id: int,
        access: AccessContext,
    ) -> tuple[Path, str]:
        """
        Return the file path and original filename, if ``access`` is
        authorized to see this document.
        """

        document = (
            self.document_repository.get_by_id_visible(
                document_id=document_id,
                access=access,
            )
        )

        if document is None:
            raise DocumentNotFoundError()

        file_path = (
            self.storage_service.get_file_path(
                document.stored_filename,
            )
        )

        return (
            file_path,
            document.filename,
        )

    def _can_delete(
        self,
        document: Document,
        access: AccessContext,
    ) -> bool:
        """
        Delete authorization -- stricter than read visibility.

        - The uploader/owner may always delete their own document,
          regardless of scope.
        - A TEAM document may additionally be deleted by a TEAM MANAGER
          of that specific team (never a plain TEAM MEMBER, and never a
          manager of a *different* team) -- this requires the per-team
          ``TeamRole``, which ``AccessContext.team_ids`` does not carry
          (it is a flat set of team ids the requester belongs to, not a
          role map), so it is resolved here via a direct, targeted
          ``TeamMembershipRepository`` lookup instead.
        - An ORGANISATION document may additionally be deleted by an
          ADMIN of that same organisation.
        - Cross-organisation access is always denied, checked before any
          scope-specific branch.
        """

        if document.user_id == access.user_id:
            return True

        if document.organisation_id != access.organisation_id:
            return False

        if document.access_scope == DocumentAccessScope.TEAM:

            if document.team_id is None or document.team_id not in access.team_ids:
                return False

            membership = self.team_membership_repository.get_membership(
                user_id=access.user_id,
                team_id=document.team_id,
            )

            return (
                membership is not None
                and membership.role == TeamRole.MANAGER
            )

        if document.access_scope == DocumentAccessScope.ORGANISATION:
            return access.role == OrgRole.ADMIN

        return False