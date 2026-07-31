from __future__ import annotations

import streamlit as st

from frontend.ui.styles import apply_global_styles
from frontend.ui.state import initialize_session_state
from frontend.ui.login import login_screen
from frontend.ui.sidebar import sidebar
from frontend.ui.sources import sources_panel
from frontend.ui.workspace import workspace


def main() -> None:

    st.set_page_config(
        page_title="Astra Study",
        page_icon="✦",
        layout="wide",
    )

    initialize_session_state()

    apply_global_styles()

    if st.session_state.token is None:
        login_screen()
        return

    left, center, right = st.columns(
        [1.15, 2.45, 1.2],
        gap="medium",
    )

    with left:
        sidebar()

    with center:
        workspace()

    with right:
        sources_panel()


if __name__ == "__main__":
    main()