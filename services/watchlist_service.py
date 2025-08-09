from dataclasses import dataclass
from typing import Set, Dict, Optional
import streamlit as st
import pandas as pd
from services.market import get_current_price


@dataclass
class WatchlistState:
    """Container for watchlist state"""
    tickers: Set[str] = None
    prices: Dict[str, float] = None

    def __post_init__(self):
        self.tickers = set() if self.tickers is None else self.tickers
        self.prices = {} if self.prices is None else self.prices


def init_watchlist() -> None:
    """Initialize watchlist state if not present"""
    if not hasattr(st.session_state, "watchlist_state"):
        st.session_state.watchlist_state = WatchlistState()


def add_to_watchlist(ticker: str) -> None:
    """Add ticker to watchlist"""
    init_watchlist()
    ticker = ticker.upper()

    if ticker in st.session_state.watchlist_state.tickers:
        st.info(f"{ticker} is already in your watchlist")
        return

    st.session_state.watchlist_state.tickers.add(ticker)


def remove_from_watchlist(ticker: str) -> None:
    """Remove ticker from watchlist"""
    init_watchlist()
    ticker = ticker.upper()
    st.session_state.watchlist_state.tickers.discard(ticker)


def get_watchlist() -> pd.DataFrame:
    """Get watchlist as DataFrame"""
    init_watchlist()
    tickers = list(st.session_state.watchlist_state.tickers)
    return pd.DataFrame({"ticker": tickers})


def load_watchlist_prices(df: pd.DataFrame) -> pd.DataFrame:
    """Update watchlist prices and calculate changes."""

    if df.empty:
        return df

    result = df.copy()
    result["current_price"] = None

    for idx, row in result.iterrows():
        price = get_current_price(row["ticker"])
        result.at[idx, "current_price"] = price

        if "last_price" in result.columns and price is not None:
            last_price = row["last_price"]
            result.at[idx, "change"] = price - last_price
            result.at[idx, "change_pct"] = ((price - last_price) / last_price) * 100

    return result
