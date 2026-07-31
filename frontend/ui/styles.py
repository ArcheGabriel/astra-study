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
--background:#f7f8fb;
--panel-bg:#ffffff;
--ink:#172033;
--muted:#69758a;
--line:#e4e8ef;
--navy:#172033;
--sky:#f3f6fb;
--accent:#3456d1;
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
min-height:100vh;
padding:0;
}

/* The markers are placed in each outer Streamlit column.  :has() keeps the
   column styling scoped even though Streamlit owns the layout DOM. */
[data-testid="stColumn"]:has(.sidebar-panel),
[data-testid="stColumn"]:has(.workspace-panel),
[data-testid="stColumn"]:has(.sources-panel){
min-height:100vh;
padding:1.25rem 1rem;
background:var(--panel-bg);
}

[data-testid="stColumn"]:has(.sidebar-panel),
[data-testid="stColumn"]:has(.workspace-panel){
border-right:1px solid var(--line);
}

/* Stretch the middle column, so its final element (the composer) can sit at
   the bottom even for an empty or short conversation. */
[data-testid="stColumn"]:has(.workspace-panel) > div > [data-testid="stVerticalBlock"]{
min-height:calc(100vh - 2.5rem);
display:flex;
flex-direction:column;
}

.layout-marker{
display:none;
}

.brand{
font-size:1.35rem;
font-weight:750;
letter-spacing:-0.04em;
color:var(--navy);
padding-top:1rem;
margin-bottom:.2rem;
}

.brand span{
color:var(--accent);
}

.login-brand{
font-size:2rem;
font-weight:750;
letter-spacing:-0.045em;
line-height:1.2;
color:var(--navy);
margin-bottom:.3rem;
}

.login-brand span{
color:var(--accent);
}

.login-top-spacer{
/* Reserve space for Streamlit's fixed app toolbar as well as the title gap. */
height:5rem;
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
margin-bottom:.2rem;
}

.chat-subtitle{
font-size:.9rem;
color:var(--muted);
margin-bottom:0;
}

.workspace-header{
border-bottom:1px solid var(--line);
padding:1rem .25rem 1rem;
margin-bottom:1rem;
}

.panel-heading{
font-size:.76rem;
font-weight:750;
letter-spacing:.08em;
text-transform:uppercase;
color:var(--muted);
padding:1rem .25rem .8rem;
border-bottom:1px solid var(--line);
margin-bottom:1rem;
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

[data-testid="stChatInput"]{
border-top:1px solid var(--line);
padding-top:1rem;
margin-top:auto;
padding-bottom:.25rem;
background:var(--panel-bg);
position:sticky;
bottom:0;
z-index:10;
}

[data-testid="stChatInput"] textarea{
border-radius:10px;
}

[data-testid="stFileUploader"]{
border:1px dashed var(--line);
border-radius:10px;
padding:.3rem;
}

</style>
        """,
        unsafe_allow_html=True,
    )
