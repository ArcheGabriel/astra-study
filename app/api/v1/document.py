from typing import Annotated

from fastapi import (
    APIRouter,
    Depends,
    File,
    Response,
    UploadFile,
    status,
)
from fastapi.responses import FileResponse

from app.dependencies.auth import get_current_user
from app.dependencies.services import get_document_service
from app.models.user import User
from app.schemas.document import DocumentResponse
from app.services.document import DocumentService

router = APIRouter(
    prefix="/documents",
    tags=["Documents"],
)


@router.post(
    "/upload",
    response_model=list[DocumentResponse],
    status_code=status.HTTP_201_CREATED,
)
async def upload_documents(
    files: list[UploadFile] = File(...),
    current_user: User = Depends(get_current_user),
    document_service: DocumentService = Depends(get_document_service),
) -> list[DocumentResponse]:
    """
    Upload one or more documents.
    """

    return await document_service.upload_documents(
        files=files,
        current_user=current_user,
    )


@router.get(
    "",
    response_model=list[DocumentResponse],
)
def get_documents(
    current_user: User = Depends(get_current_user),
    document_service: DocumentService = Depends(get_document_service),
) -> list[DocumentResponse]:
    """
    Retrieve all uploaded documents.
    """

    return document_service.get_documents(
        current_user=current_user,
    )


@router.get(
    "/{document_id}",
    response_model=DocumentResponse,
)
def get_document(
    document_id: int,
    current_user: User = Depends(get_current_user),
    document_service: DocumentService = Depends(get_document_service),
) -> DocumentResponse:
    """
    Retrieve a single document.
    """

    return document_service.get_document(
        document_id=document_id,
        current_user=current_user,
    )


@router.get(
    "/{document_id}/download",
)
def download_document(
    document_id: int,
    current_user: User = Depends(get_current_user),
    document_service: DocumentService = Depends(get_document_service),
) -> FileResponse:
    """
    Download a document.
    """

    file_path, filename = (
        document_service.download_document(
            document_id=document_id,
            current_user=current_user,
        )
    )

    return FileResponse(
        path=file_path,
        filename=filename,
        media_type="application/octet-stream",
    )


@router.delete(
    "/{document_id}",
    status_code=status.HTTP_204_NO_CONTENT,
)
async def delete_document(
    document_id: int,
    current_user: User = Depends(get_current_user),
    document_service: DocumentService = Depends(get_document_service),
) -> Response:
    """
    Delete a document.
    """

    await document_service.delete_document(
        document_id=document_id,
        current_user=current_user,
    )

    return Response(
        status_code=status.HTTP_204_NO_CONTENT,
    )