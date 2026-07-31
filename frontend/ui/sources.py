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

    for index, citation in enumerate(
        citations,
        start=1,
    ):

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

        score = getattr(
            citation,
            "score",
            None,
        )

        with st.expander(
            f"{index}. {source}",
            expanded=False,
        ):

            if page is not None:
                st.write(
                    f"**Page:** {page}"
                )

            if section:
                st.write(
                    f"**Section:** {section}"
                )

            if score is not None:
                st.write(
                    f"**Score:** {score:.4f}"
                )

            excerpt = getattr(
                citation,
                "text",
                None,
            )

            if excerpt:

                st.markdown("---")

                st.write(
                    excerpt
                )


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

    panel = st.container()

    with panel:

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