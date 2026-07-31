from __future__ import annotations

import streamlit as st


def apply_global_styles() -> None:
    """
    Apply Astra Study global stylesheet.
    """

    st.markdown(
        """
<style>

:root{
--background:#f8fafc;
--panel-bg:white;
--ink:#16213a;
--muted:#71809b;
--line:#e7ebf2;
--navy:#172b4d;
--sky:#eef5ff;
--accent:#4169e1;
}

@media (prefers-color-scheme: dark) {
  :root {
    --background:#0e131f;
    --panel-bg:#1a2333;
    --ink:#f8fafc;
    --muted:#94a3b8;
    --line:#2e3c54;
    --navy:#f1f5f9;
    --sky:#16213a;
    --accent:#3b82f6;
  }
}

.stApp{
background:var(--background);
color:var(--ink);
}

header,
footer,
#MainMenu{
display:none;
}

.block-container{
max-width:none;
width:100%;
padding-top:0.5rem;
padding-left:0.5rem;
padding-right:0.5rem;
padding-bottom:0.5rem;
}

.panel{
background:var(--panel-bg);
border:1px solid var(--line);
border-radius:18px;
padding:1.25rem;
box-shadow:0 5px 20px rgba(20,41,82,.035);
}

.brand{
font-size:1.35rem;
font-weight:750;
letter-spacing:-0.04em;
color:var(--navy);
margin-bottom:.2rem;
}

.brand span{
color:var(--accent);
}

.eyebrow{
font-size:.76rem;
font-weight:700;
letter-spacing:.08em;
text-transform:uppercase;
color:var(--muted);
margin-top:1.5rem;
margin-bottom:.55rem;
}

.chat-title{
font-size:1.12rem;
font-weight:700;
color:var(--navy);
margin-bottom:.15rem;
}

.chat-subtitle{
font-size:.9rem;
color:var(--muted);
margin-bottom:1.2rem;
}

.source-card{
border:1px solid var(--line);
border-radius:12px;
padding:.85rem;
margin-bottom:.7rem;
background:var(--panel-bg);
}

.source-name{
font-weight:700;
color:var(--navy);
}

.source-meta{
font-size:.8rem;
color:var(--muted);
margin-top:.25rem;
}

.confidence{
margin-top:.35rem;
font-size:.72rem;
font-weight:700;
color:#198754;
}

.empty-state{
text-align:center;
padding:4rem 1rem;
color:var(--muted);
}

.stButton>button{
border-radius:10px;
font-weight:600;
}

[data-testid="stChatMessage"]{
padding-top:.35rem;
padding-bottom:.35rem;
}

</style>
        """,
        unsafe_allow_html=True,
    )