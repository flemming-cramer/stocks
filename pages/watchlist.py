from pathlib import Path
from datetime import datetime

import pandas as pd
import streamlit as st

from components.nav import navbar
from services.market import fetch_price, fetch_prices
from services.session import get_watchlist, add_to_watchlist
from forms import LogABuy


@st.experimental_memo(ttl=1800)
def _load_prices(tickers: list[str]) -> pd.DataFrame:
    """Fetch market data for ``tickers`` and cache it for 30 minutes."""

    return fetch_prices(tickers)


def recommend_tickers(portfolio, watchlist: list[str]) -> list[str]:
    """Return a list of up to five suggested tickers.

    This is a placeholder that simply suggests popular large-cap stocks not
    already in the portfolio or watchlist. The recommendation logic can be
    expanded to analyse industry peers and top movers.
    """

    universe = [
        "AAPL",
        "MSFT",
        "GOOGL",
        "AMZN",
        "TSLA",
        "NVDA",
        "META",
        "NFLX",
        "INTC",
        "AMD",
    ]
    portfolio_tickers: set[str] = set()
    try:
        portfolio_tickers = set(portfolio.get("Ticker", []))
    except Exception:
        pass
    return [t for t in universe if t not in watchlist and t not in portfolio_tickers][:5]


def watchlist_page() -> None:
    """Render the watchlist management page."""

    st.set_page_config(
        page_title="Watchlist",
        layout="wide",
        initial_sidebar_state="expanded",
    )
    navbar(Path(__file__).name)

    st.header("Watchlist")

    new_ticker = st.text_input("Add ticker to watchlist")
    if st.button("Add"):
        add_to_watchlist(new_ticker.upper())
        st.experimental_rerun()

    watchlist = get_watchlist()

    price_data = _load_prices(watchlist) if watchlist else pd.DataFrame()

    if not price_data.empty:
        st.caption(f"Prices as of {datetime.now():%Y-%m-%d %H:%M:%S}")

    header_cols = st.columns([2, 2, 2, 2, 2, 1])
    header_cols[0].write("Ticker")
    header_cols[1].write("Current Price")
    header_cols[2].write("Day % Change")
    header_cols[3].write("Market Value")
    header_cols[4].write("Stop-Loss")
    header_cols[5].write("")

    if watchlist and not price_data.empty:
        if isinstance(price_data.columns, pd.MultiIndex):
            closes = price_data["Close"].iloc[-1]
            opens = price_data["Open"].iloc[0]
            for ticker in watchlist:
                close = float(closes.get(ticker, float("nan")))
                open_ = float(opens.get(ticker, float("nan")))
                change = (close - open_) / open_ * 100 if open_ else float("nan")
                cols = st.columns([2, 2, 2, 2, 2, 1])
                cols[0].write(ticker)
                cols[1].write(f"${close:.2f}" if not pd.isna(close) else "N/A")
                cols[2].write(f"{change:.2f}%" if not pd.isna(change) else "N/A")
                cols[3].write("-")
                cols[4].write("-")
                if cols[5].button(f"Buy {ticker}", key=f"buy_{ticker}"):
                    with st.modal(f"Buy {ticker}"):
                        LogABuy(ticker_default=ticker)
        else:
            close = float(price_data["Close"].iloc[-1])
            open_ = float(price_data["Open"].iloc[0])
            change = (close - open_) / open_ * 100 if open_ else float("nan")
            ticker = watchlist[0]
            cols = st.columns([2, 2, 2, 2, 2, 1])
            cols[0].write(ticker)
            cols[1].write(f"${close:.2f}" if not pd.isna(close) else "N/A")
            cols[2].write(f"{change:.2f}%" if not pd.isna(change) else "N/A")
            cols[3].write("-")
            cols[4].write("-")
            if cols[5].button(f"Buy {ticker}", key=f"buy_{ticker}"):
                with st.modal(f"Buy {ticker}"):
                    LogABuy(ticker_default=ticker)
    else:
        st.info("Your watchlist is empty.")

    with st.expander("Suggested Tickers"):
        if st.button("Recommend Tickers"):
            portfolio = st.session_state.get("portfolio")
            suggestions = recommend_tickers(portfolio, watchlist)
            for sym in suggestions:
                s_cols = st.columns([3, 1])
                s_cols[0].write(sym)
                if s_cols[1].button("Add", key=f"add_{sym}"):
                    add_to_watchlist(sym)
                    st.experimental_rerun()


if __name__ == "__main__":
    watchlist_page()
