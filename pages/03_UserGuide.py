"""User guide page for the application."""

from pathlib import Path

import streamlit as st

from components.nav import navbar
from ui.user_guide import render_user_guide


st.set_page_config(
    page_title="User Guide",
    layout="wide",
    initial_sidebar_state="expanded",
)

navbar(Path(__file__).name)

st.header("User Guide")

render_user_guide()

