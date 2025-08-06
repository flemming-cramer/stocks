"""Navigation bar component used across pages."""

from pathlib import Path

import streamlit as st


def navbar(active_page: str) -> None:
    """Render a horizontal navigation bar and hide default sidebar links.

    Parameters
    ----------
    active_page:
        Name of the current file (e.g. ``Path(__file__).name``).
    """

    st.markdown(
        """
        <style>
            [data-testid="stSidebarNav"] {display: none;}
            .nav-container {
                display: flex;
                gap: 2rem;
                padding-bottom: 0.25rem;
            }
            .nav-link {
                text-decoration: none;
                color: inherit;
                border-bottom: 3px solid transparent;
                padding-bottom: 0.25rem;
            }
            .nav-link:hover {
                border-bottom: 3px solid #999999;
            }
            .nav-link.active {
                font-weight: bold;
                border-bottom: 3px solid red;
            }
        </style>
        """,
        unsafe_allow_html=True,
    )

    nav = st.container()
    with nav:
        st.markdown(
            f"""
            <div class="nav-container">
                <a class="nav-link {'active' if active_page == Path('app.py').name else ''}" href="/" target="_self">Portfolio</a>
                <a class="nav-link {'active' if active_page == Path('pages/02_Performance.py').name else ''}" href="/Performance" target="_self">Performance</a>
            </div>
            <hr />
            """,
            unsafe_allow_html=True,
        )


