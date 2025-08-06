"""Streamlit app for local portfolio tracking and AI‑assisted trading."""

from pathlib import Path

import streamlit as st
from streamlit import config as _config

from components.nav import navbar
from ui.dashboard import render_dashboard

st.set_page_config(
    page_title="AI Assisted Trading",
    layout="wide",
    initial_sidebar_state="expanded",
)

navbar(Path(__file__).name)

st.header("Portfolio Dashboard")


def main() -> None:
    """Application entry point."""

    render_dashboard()


if __name__ == "__main__":
    main()
