from __future__ import annotations

import base64

import streamlit as st

from frontend.api.api_client import ApiClient, ApiException
from frontend.api.document_service import DocumentService
from frontend.models.document import Document


def _client() -> ApiClient:
    """
    Create an authenticated API client.
    """

    return ApiClient(
        base_url=st.session_state.api_url,
        access_token=st.session_state.token,
    )


def _document_service() -> DocumentService:
    """
    Create the document service.
    """

    return DocumentService(
        _client(),
    )


def _render_document_preview(
    document: Document,
) -> None:
    """
    Render the selected document.
    """

    st.write(
        f"**{document.filename}**"
    )

    st.caption(
        f"Status: {document.status}"
    )

    if not st.button(
        "Open Document",
        key=f"preview_{document.id}",
        use_container_width=True,
    ):
        return

    try:

        file_bytes = (
            _document_service().download_document(
                document.id
            )
        )

        #
        # PDF Preview
        #

        if (
            document.content_type
            == "application/pdf"
        ):

            encoded = base64.b64encode(
                file_bytes
            ).decode()

            st.markdown(
                f"""
<iframe
src="data:application/pdf;base64,{encoded}"
width="100%"
height="650">
</iframe>
""",
                unsafe_allow_html=True,
            )

            return

        #
        # Images
        #

        if document.content_type.startswith(
            "image/"
        ):

            st.image(
                file_bytes,
                use_container_width=True,
            )

            return

        #
        # Everything else
        #

        st.download_button(
            "Download Document",
            data=file_bytes,
            file_name=document.filename,
            mime=document.content_type,
            use_container_width=True,
        )

    except ApiException as exc:

        st.error(
            str(exc)
        )


def _normalize_heading_path(heading_path: list[str] | None) -> list[str]:
    """
    Presentation-only cleanup: collapse consecutive duplicate heading
    entries (e.g. a top-level heading repeated verbatim as its own
    immediate child) so "Executive Summary -> Executive Summary" reads as
    "Executive Summary". The raw heading_path sent by the backend is never
    modified -- only what is displayed here.
    """

    if not heading_path:
        return []

    normalized: list[str] = []

    for heading in heading_path:
        if not normalized or normalized[-1] != heading:
            normalized.append(heading)

    return normalized


def _render_citations() -> None:
    """
    Display retrieved citations.
    """

    citations = st.session_state.citations

    if not citations:
        return

    st.subheader(
        "Retrieved Sources"
    )

    unique: list = []
    seen: set[tuple] = set()
    for citation in citations:
        key = (getattr(citation, "source", None), getattr(citation, "page", None),
               getattr(citation, "section", None), getattr(citation, "sheet_name", None),
               getattr(citation, "chunk_id", None))
        if key not in seen:
            seen.add(key)
            unique.append(citation)

    for index, citation in enumerate(unique, start=1):

        source = getattr(
            citation,
            "source",
            "Unknown Source",
        )

        page = getattr(
            citation,
            "page",
            None,
        )

        section = getattr(
            citation,
            "section",
            None,
        )

        sheet_name = getattr(citation, "sheet_name", None)
        block_type = getattr(citation, "block_type", None)
        page_end = getattr(citation, "page_end", None)
        parser = getattr(citation, "parser", None)
        heading_path = _normalize_heading_path(
            getattr(citation, "heading_path", None)
        )
        chunk_id = getattr(citation, "chunk_id", None)

        score = getattr(citation, "score", None)
        answer_support = getattr(citation, "answer_support", None)

        with st.expander(
            f"{index}. {source}",
            expanded=False,
        ):

            if page is not None:
                is_range = page_end is not None and page_end != page
                label = f"{page}–{page_end}" if is_range else f"{page}"
                st.write(f"**{'Pages' if is_range else 'Page'}:** {label}")

            if sheet_name:
                st.write(f"**Sheet:** {sheet_name}")

            if heading_path:
                st.write(
                    "**Location:** " + " › ".join(heading_path)
                )
            elif section:
                st.write(f"**Section:** {section}")

            if block_type:
                st.write(f"**Content type:** {block_type.replace('_', ' ').title()}")

            excerpt = getattr(citation, "excerpt", None) or getattr(
                citation, "text", None
            )

            if excerpt:
                st.markdown("---")
                st.write(f"*“{excerpt}”*")

            details = []
            if parser:
                details.append(f"Parser: {parser}")
            if score is not None:
                details.append(f"Reranker score: {score:.4f}")
            if answer_support is not None:
                details.append(f"Answer overlap: {answer_support:.2f}")
            if chunk_id:
                details.append(f"Chunk: {chunk_id[:8]}…")
            if details:
                st.caption(" · ".join(details))


def _render_uploaded_documents() -> None:
    """
    Display uploaded documents.
    """

    documents: list[Document] = (
        st.session_state.documents
    )

    st.subheader(
        "Uploaded Documents"
    )

    if not documents:

        st.info(
            "No documents uploaded."
        )

        return

    for document in documents:

        if st.button(
            f"📄 {document.filename}",
            key=f"doc_sources_{document.id}",
            use_container_width=True,
        ):

            st.session_state.active_document = (
                document
            )

            st.rerun()


def sources_panel() -> None:
    """
    Render the right-side panel.
    """

    st.markdown(
        '<span class="layout-marker sources-panel"></span>',
        unsafe_allow_html=True,
    )

    panel = st.container()

    with panel:

        st.markdown(
            '<div class="panel-heading">Sources</div>',
            unsafe_allow_html=True,
        )

        _render_citations()

        st.divider()

        _render_uploaded_documents()

        st.divider()

        document = (
            st.session_state.active_document
        )

        if document is not None:

            st.subheader(
                "Document Preview"
            )

            _render_document_preview(
                document
            )
