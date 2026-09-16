from pathlib import Path

from fastapi import UploadFile

from app.enums.document import DocumentAccessScope, DocumentStatus
from app.enums.organisation import OrgRole
from app.enums.team import TeamRole
from app.exceptions.document import (
    DocumentNotFoundError,
    InvalidAccessScopeError,
    OrganisationScopeForbiddenError,
    TeamMembershipRequiredError,
    TeamNotFoundError,
)
from app.models.document import Document
from app.repositories.document import DocumentRepository
from app.repositories.team import TeamRepository
from app.repositories.team_membership import TeamMembershipRepository
from app.retrieval.access import AccessContext
from app.schemas.document import DocumentResponse
from app.search.dense.repository import DenseRepository
from app.storage.base import BaseStorageService
from app.validators.document import DocumentValidator


class DocumentService:
    """
    Handles document upload, read, and delete business logic.

    Create/read/delete authorization is all based on the trusted
    ``AccessContext`` (identity, role, organisation, team membership) --
    never on ``document_id``/``team_id``/``organisation_id`` alone, and
    never on client-supplied ``organisation_id`` (see ``upload_documents``
    / ``_can_create``).
    """

    def __init__(
        self,
        document_repository: DocumentRepository,
        storage_service: BaseStorageService,
        team_membership_repository: TeamMembershipRepository,
        dense_repository: DenseRepository,
        team_repository: TeamRepository,
    ) -> None:
        self.document_repository = document_repository
        self.storage_service = storage_service
        self.team_membership_repository = team_membership_repository
        self.dense_repository = dense_repository
        self.team_repository = team_repository

    async def upload_documents(
        self,
        *,
        files: list[UploadFile],
        access: AccessContext,
        access_scope: str | None = None,
        team_id: int | None = None,
    ) -> list[Document]:
        """
        Upload one or more documents under one, single authorized scope.

        Scope/team authorization (``_can_create``) runs once, before any
        file is validated or stored -- an unauthorized request creates
        nothing, and every file in the batch is created under the same
        authorized ``access_scope``/``team_id`` (there is no per-file
        scope override).

        ``access_scope`` is the raw client-supplied value (``None`` when
        omitted, matching today's INDIVIDUAL-only clients exactly);
        ``organisation_id`` is never accepted from the caller at all --
        it always comes from ``access.organisation_id``.

        Returns the created Document models.
        """

        resolved_scope, resolved_team_id = self._can_create(
            access=access,
            access_scope=access_scope,
            team_id=team_id,
        )

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
                user_id=access.user_id,
                organisation_id=access.organisation_id,
                team_id=resolved_team_id,
                access_scope=resolved_scope,
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

    def _can_create(
        self,
        *,
        access: AccessContext,
        access_scope: str | None,
        team_id: int | None,
    ) -> tuple[DocumentAccessScope, int | None]:
        """
        CREATE-time authorization. Returns the validated
        ``(access_scope, team_id)`` pair to persist, or raises.

        - INDIVIDUAL: allowed for every authenticated user; ``team_id``
          must not be supplied.
        - TEAM: allowed for any role (``OrgRole`` MEMBER/MANAGER/ADMIN,
          ``TeamRole`` MEMBER/MANAGER all qualify -- deliberate product
          decision, TEAM creation is a membership check, not a role
          check) provided the requester is an actual member of a
          ``team_id`` that exists in their own organisation.
        - ORGANISATION: ``access.role == OrgRole.ADMIN`` only;
          ``team_id`` must not be supplied.

        ``organisation_id`` is never a parameter here -- every branch
        persists ``access.organisation_id``, never anything client
        supplied.
        """

        if access_scope is None:
            resolved_scope = DocumentAccessScope.INDIVIDUAL
        else:
            try:
                resolved_scope = DocumentAccessScope(access_scope)
            except ValueError:
                raise InvalidAccessScopeError(
                    f"Unrecognised access_scope: {access_scope!r}."
                ) from None

        if resolved_scope == DocumentAccessScope.INDIVIDUAL:

            if team_id is not None:
                raise InvalidAccessScopeError(
                    "team_id must not be supplied for an INDIVIDUAL document."
                )

            return resolved_scope, None

        if resolved_scope == DocumentAccessScope.TEAM:

            if team_id is None:
                raise InvalidAccessScopeError(
                    "team_id is required for a TEAM document."
                )

            team = self.team_repository.get_by_id(team_id)

            # Nonexistent team and cross-organisation team collapse into
            # the same response -- see TeamNotFoundError's docstring --
            # so a requester can never enumerate another organisation's
            # teams by probing team_id values.
            if team is None or team.organisation_id != access.organisation_id:
                raise TeamNotFoundError()

            membership = self.team_membership_repository.get_membership(
                user_id=access.user_id,
                team_id=team.id,
            )

            # Membership is checked regardless of TeamRole -- MEMBER and
            # MANAGER both qualify; only *actual* membership matters.
            if membership is None:
                raise TeamMembershipRequiredError()

            return resolved_scope, team.id

        # resolved_scope == DocumentAccessScope.ORGANISATION

        if team_id is not None:
            raise InvalidAccessScopeError(
                "team_id must not be supplied for an ORGANISATION document."
            )

        if access.role != OrgRole.ADMIN:
            raise OrganisationScopeForbiddenError()

        return resolved_scope, None

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