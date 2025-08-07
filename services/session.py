import streamlit as st

from config import WATCHLIST_FILE
from data.portfolio import load_portfolio
from data.watchlist import load_watchlist, save_watchlist


def init_session_state() -> None:
    """Initialise default values in ``st.session_state`` on first run."""

    for key, default in {
        "b_ticker": "",
        "b_shares": 1.0,
        "b_price": 1.0,
        "b_stop_pct": 0.0,
        "s_ticker": "",
        "s_shares": 1.0,
        "s_price": 1.0,
        "ac_amount": 0.0,
        "lookup_symbol": "",
        "watchlist_feedback": None,
        "watchlist": [],
        "watchlist_prices": {},
        "show_cash_form": False,
        "daily_summary": "",
        "show_info": True,
    }.items():
        st.session_state.setdefault(key, default)

    if "portfolio" not in st.session_state:
        port, cash, needs_cash = load_portfolio()
        st.session_state.portfolio = port
        st.session_state.cash = cash
        st.session_state.needs_cash = needs_cash

    if not st.session_state.watchlist and WATCHLIST_FILE.exists():
        st.session_state.watchlist = load_watchlist()


def get_watchlist() -> list[str]:
    """Return the current watchlist from ``st.session_state``."""

    return st.session_state.get("watchlist", [])


def add_to_watchlist(ticker: str) -> None:
    """Add ``ticker`` to the watchlist and persist it."""

    watchlist = st.session_state.setdefault("watchlist", [])
    symbol = ticker.upper()
    if symbol and symbol not in watchlist:
        watchlist.append(symbol)
        save_watchlist(watchlist)


def remove_from_watchlist(symbol: str) -> None:
    """Remove a ticker symbol from the watchlist in session state and persistent storage."""

    # Load the current list
    watchlist = get_watchlist()
    # Remove if present
    if symbol in watchlist:
        watchlist.remove(symbol)
        # Persist the updated list
        save_watchlist(watchlist)
        # Update session state if needed
        import streamlit as st
        st.session_state.watchlist = watchlist
