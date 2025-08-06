from pathlib import Path
import streamlit as st


def navbar(active_page: str) -> None:
    """Render top navigation bar and hide sidebar navigation.

    Parameters
    ----------
    active_page: str
        The filename of the current page. Used to style the active link.
    """
    st.markdown(
        """
        <style>
            [data-testid="stSidebarNav"] {display: none;}
            div[data-testid="stColumn"] > div > a[data-testid="stPageLink"] {
                text-decoration: none;
                color: inherit;
                padding-right: 1rem;
            }
        </style>
        """,
        unsafe_allow_html=True,
    )

    nav = st.container()
    with nav:
        col1, col2 = st.columns(2)
        if Path("app.py").name == active_page:
            col1.markdown(
                "<span style='font-weight:bold; color:red;'>Portfolio</span>",
                unsafe_allow_html=True,
            )
        else:
            col1.page_link("app.py", label="Portfolio")

        if Path("pages/02_Performance.py").name == active_page:
            col2.markdown(
                "<span style='font-weight:bold; color:red;'>Performance</span>",
                unsafe_allow_html=True,
            )
        else:
            col2.page_link("pages/02_Performance.py", label="Performance")
    nav.markdown("<hr />", unsafe_allow_html=True)
