import streamlit as st
import pandas as pd

from config import COL_TICKER, COL_SHARES, COL_PRICE
from services.market import fetch_price
from services.trading import manual_buy, manual_sell


def validate_buy_form(data: dict) -> bool:
    """Validate buy form data."""
    try:
        # Check required fields
        if not data.get("ticker"):
            st.error("Ticker symbol is required")
            return False

        shares = float(data.get("shares", 0))
        price = float(data.get("price", 0))
        
        if shares <= 0:
            st.error("Number of shares must be positive")
            return False
            
        if price <= 0:
            st.error("Price must be positive")
            return False

        total_cost = shares * price
        if total_cost > st.session_state.cash:
            st.error("Insufficient funds for purchase")
            return False

        return True

    except (ValueError, TypeError):
        st.error("Invalid number format")
        return False


def validate_sell_form(data: dict) -> bool:
    """
    Validate sell form data.
    Returns True if valid, False otherwise.
    """
    if not data.get("ticker"):
        st.error("Ticker symbol is required")
        return False

    try:
        shares = float(data.get("shares", 0))
        price = float(data.get("price", 0))

        if shares <= 0:
            st.error("Number of shares must be positive")
            return False

        if price <= 0:
            st.error("Price must be positive")
            return False

        # Check if we have enough shares
        portfolio = st.session_state.portfolio
        matching = portfolio[portfolio["Ticker"] == data["ticker"]]
        if matching.empty or matching.iloc[0]["Shares"] < shares:
            st.error("Insufficient shares for this sale")
            return False

        return True

    except ValueError:
        st.error("Invalid number format")
        return False


def show_buy_form(ticker_default: str = "") -> None:
    """Render and process the buy form inside an expander.

    Parameters
    ----------
    ticker_default: str, optional
        When provided, pre-populates the ticker input with this value.
    """

    def submit_buy() -> None:
        if st.session_state.b_shares <= 0 or st.session_state.b_price <= 0:
            st.session_state.feedback = (
                "error",
                "Shares and price must be positive.",
            )
            return
        ok, msg, port, cash = manual_buy(
            st.session_state.b_ticker,
            st.session_state.b_shares,
            st.session_state.b_price,
            st.session_state.b_price * (1 - st.session_state.b_stop_pct / 100)
            if st.session_state.b_price > 0 and st.session_state.b_stop_pct > 0
            else 0.0,
            st.session_state.portfolio,
            st.session_state.cash,
        )
        if ok:
            st.session_state.portfolio = port
            st.session_state.cash = cash
            st.session_state.feedback = ("success", msg)
            st.session_state.pop("b_ticker", None)
            st.session_state.pop("b_shares", None)
            st.session_state.pop("b_price", None)
            st.session_state.pop("b_stop_pct", None)
        else:
            st.session_state.feedback = ("error", msg)

    with st.expander("Log a Buy"):
        with st.form("buy_form", clear_on_submit=True):
            st.text_input(
                "Ticker",
                key="b_ticker",
                placeholder="e.g. AAPL",
                value=ticker_default,
            )
            st.number_input(
                "Shares",
                min_value=1,
                value=1,
                step=1,
                key="b_shares",
            )
            st.number_input(
                "Price",
                min_value=0.0,
                value=0.0,
                step=0.01,
                format="%.2f",
                key="b_price",
            )
            st.number_input(
                "Stop-loss %",
                min_value=0.0,
                value=0.0,
                max_value=100.0,
                step=0.1,
                format="%.1f",
                key="b_stop_pct",
            )
            if st.session_state.b_price > 0 and st.session_state.b_stop_pct > 0:
                calc_stop = st.session_state.b_price * (
                    1 - st.session_state.b_stop_pct / 100
                )
                st.caption(f"Stop loss price: ${calc_stop:.2f}")
            st.form_submit_button("Submit Buy", on_click=submit_buy)


def show_sell_form() -> None:
    """Render and process the sell form inside an expander."""

    def submit_sell() -> None:
        if st.session_state.s_shares <= 0 or st.session_state.s_price <= 0:
            st.session_state.feedback = (
                "error",
                "Shares and price must be positive.",
            )
            return
        ok, msg, port, cash = manual_sell(
            st.session_state.s_ticker,
            st.session_state.s_shares,
            st.session_state.s_price,
            st.session_state.portfolio,
            st.session_state.cash,
        )
        if ok:
            st.session_state.portfolio = port
            st.session_state.cash = cash
            st.session_state.feedback = ("success", msg)
            # Clear form values
            st.session_state.pop("s_ticker", None)
            st.session_state.pop("s_shares", None)
            st.session_state.pop("s_price", None)
        else:
            st.session_state.feedback = ("error", msg)

    with st.expander("Log a Sell"):
        holdings = st.session_state.portfolio
        if holdings.empty:
            st.info("You have no holdings to sell.")
            return

        # Build options with a placeholder
        tickers = ["Select a Ticker"] + sorted(
            st.session_state.portfolio[COL_TICKER].unique().tolist()
        )

        # Render the selectbox with placeholder default
        selected = st.selectbox(
            "Ticker",
            options=tickers,
            index=0,  # Force default selection to "Select a Ticker"
        )

        # Only proceed if a real ticker is selected
        if selected == "Select a Ticker":
            st.warning("Please choose a ticker from your portfolio before selling.")
            return

        matching = st.session_state.portfolio[
            st.session_state.portfolio[COL_TICKER] == selected
        ]

        # Check if matching shares exist before proceeding
        if matching.empty:
            st.error(f"No shares found for {selected}")
            return

        max_shares = int(matching.iloc[0][COL_SHARES])
        latest_price = float(matching.iloc[0][COL_PRICE])
        fetched_price = fetch_price(selected)
        price_default = fetched_price if fetched_price is not None else latest_price

        # Determine min/default values
        share_min = 1 if max_shares > 0 else 0
        share_default = 1 if max_shares > 0 else 0

        if max_shares == 0:
            st.info("You have no shares to sell for this ticker.")
            return

        # Only render the form when shares are available
        with st.form("sell_form", clear_on_submit=True):
            st.number_input(
                "Shares to sell",
                min_value=share_min,
                value=share_default,
                max_value=max_shares,
                step=1,
                key="s_shares",
            )
            st.number_input(
                "Price",
                min_value=0.0,
                value=price_default,
                step=0.01,
                format="%.2f",
                key="s_price",
            )
            st.form_submit_button("Submit Sell", on_click=submit_sell)


