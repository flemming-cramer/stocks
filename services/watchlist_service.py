import math
import streamlit as st

from data.watchlist import save_watchlist
from services.market import fetch_prices


@st.cache_data(ttl=1800)
def load_watchlist_prices(tickers: list[str]) -> dict[str, float]:
    """Fetch and parse latest prices for ``tickers``."""

    data = fetch_prices(tickers)
    prices: dict[str, float] = {}
    if data.empty:
        return prices

    if data.columns.nlevels > 1:
        close = data["Close"].iloc[-1]
        for t in tickers:
            val = close.get(t)
            if val is None:
                continue
            try:
                price = float(val)
            except (TypeError, ValueError):
                continue
            if not math.isnan(price):
                prices[t] = price
    else:
        if tickers:
            val = data["Close"].iloc[-1]
            try:
                price = float(val)
            except (TypeError, ValueError):
                pass
            else:
                if not math.isnan(price):
                    prices[tickers[0]] = price

    return prices


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

    watchlist = get_watchlist()
    if symbol in watchlist:
        watchlist.remove(symbol)
        save_watchlist(watchlist)
        st.session_state.watchlist = watchlist
