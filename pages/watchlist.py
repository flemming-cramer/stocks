from pathlib import Path

import streamlit as st

st.set_page_config(
    page_title="Watchlist",
    layout="wide",
    initial_sidebar_state="collapsed",
)

# Hide the default sidebar completely
st.markdown(
    """
    <style>
        section[data-testid="stSidebar"] { display: none; }
        button[aria-label="Main menu"] { display: none; }
    </style>
    """,
    unsafe_allow_html=True,
)

from components.nav import navbar
from services.session import get_watchlist, add_to_watchlist, remove_from_watchlist
from services.market import fetch_price
from ui.forms import LogABuy


@st.cache_data(ttl=1800)
def load_watchlist_prices(tickers: list[str]) -> dict[str, dict]:
    prices = {}
    for t in tickers:
        try:
            prices[t] = fetch_price(t)
        except Exception:
            # skip invalid or missing tickers
            continue
    return prices


def watchlist_page():
    navbar(Path(__file__).name)
    st.title("Watchlist")

    # Add-ticker input with placeholder
    new_ticker = st.text_input(
        "Add ticker to watchlist",
        placeholder="Enter ticker symbol. E.g. AAPL",
    )
    if st.button("Add"):
        symbol = new_ticker.strip().upper()
        if symbol:
            try:
                fetch_price(symbol)
            except Exception as e:
                st.error(f"Could not add {symbol}: {e}")
            else:
                add_to_watchlist(symbol)
                st.experimental_rerun()

    # Load current watchlist and prices
    watchlist = get_watchlist()
    prices = load_watchlist_prices(watchlist)

    # Render table header
    st.markdown("## Current Watchlist")
    cols = st.columns([3, 2, 2, 1, 1])
    cols[0].markdown("**Ticker**")
    cols[1].markdown("**Price**")
    cols[2].markdown("**Change %**")
    cols[3].markdown("**Delete**")
    cols[4].markdown("**Buy**")

    # Loop through tickers
    for ticker in watchlist:
        price_info = prices.get(ticker)
        if not price_info:
            continue
        price = price_info.get("price")
        change_pct = price_info.get("change_pct")
        row_cols = st.columns([3, 2, 2, 1, 1])
        row_cols[0].write(ticker)
        row_cols[1].write(f"${price:.2f}")
        row_cols[2].write(f"{change_pct:.2f}%")
        if row_cols[3].button("❌", key=f"del_{ticker}"):
            remove_from_watchlist(ticker)
            st.experimental_rerun()
        if row_cols[4].button("Buy", key=f"buy_{ticker}"):
            with st.modal(f"Buy {ticker}"):
                LogABuy(ticker_default=ticker)

if __name__ == "__main__":
    watchlist_page()
