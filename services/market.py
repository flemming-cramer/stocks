import pandas as pd
import yfinance as yf
import streamlit as st

from services.logging import log_error


def _register_provider_issue(message: str) -> None:
    """Record provider issue messages in the Streamlit session state so the UI
    can surface notifications to users. In non-Streamlit contexts this is a no-op.
    """
    try:
        issues = st.session_state.setdefault("provider_issues", [])
        issues.append(message)
    except Exception:
        # If session state isn't available (e.g. in some test contexts), ignore.
        pass


@st.cache_data(ttl=300)
def fetch_price(ticker: str) -> float | None:
    """Return the latest close price for ``ticker`` or ``None`` on failure.

    This first attempts the primary provider (yfinance). If the provider fails
    or returns no data, we try a lightweight fallback using cached prices from
    the Streamlit session (if available) and register a provider issue so the
    UI can notify the user.
    """

    try:  # pragma: no cover - network errors
        data = yf.download(ticker, period="1d", progress=False)
        if not data.empty:
            return float(data["Close"].iloc[-1])
        # No data returned; return None (keep previous behaviour)
        return None
    except Exception as exc:
        # Keep the original, short log message for tests and users
        log_error(f"Failed to fetch price for {ticker}")
        _register_provider_issue(f"Failed to fetch price for {ticker}: {exc}")

    # Fallback: try using cached prices available in session state
    try:
        cached = st.session_state.get("watchlist_prices", {})
        if ticker in cached:
            return float(cached[ticker])
        # Try portfolio snapshot
        portfolio = st.session_state.get("portfolio")
        if portfolio is not None and not portfolio.empty and "symbol" in portfolio.columns and "price" in portfolio.columns:
            row = portfolio.loc[portfolio["symbol"] == ticker]
            if not row.empty:
                return float(row["price"].iloc[0])
    except Exception:
        # Be quiet in fallback; we already logged the provider problem above.
        pass

    return None


@st.cache_data(ttl=300)
def fetch_prices(tickers: list[str]) -> pd.DataFrame:
    """Return daily data for ``tickers`` in a single request.

    Falls back to constructing a small DataFrame from cached session prices
    when the primary provider fails.
    """

    if not tickers:
        return pd.DataFrame()

    try:  # pragma: no cover - network errors
        df = yf.download(tickers, period="1d", progress=False)
        if df is not None and not df.empty:
            return df
        # No data returned; return empty DataFrame (keep previous behaviour)
        return pd.DataFrame()
    except Exception as exc:
        # Keep original short log message for compatibility with tests
        log_error(f"Failed to fetch prices for {', '.join(tickers)}")
        _register_provider_issue(f"Failed to fetch prices for {', '.join(tickers)}: {exc}")

    # Build a tiny DataFrame from cached session prices when possible
    try:
        cached = st.session_state.get("watchlist_prices", {})
        rows = []
        for t in tickers:
            if t in cached:
                rows.append({"Ticker": t, "Close": cached[t]})
        if rows:
            return pd.DataFrame(rows).set_index("Ticker")
    except Exception:
        pass

    return pd.DataFrame()


def get_day_high_low(ticker: str) -> tuple[float, float]:
    """Return today's high and low price for ``ticker``."""

    try:
        data = yf.download(ticker, period="1d", progress=False)
    except Exception as exc:  # pragma: no cover - network errors
        _register_provider_issue(f"Data download failed for {ticker}: {exc}")
        raise RuntimeError(f"Data download failed: {exc}") from exc
    if data.empty:
        raise ValueError("No market data available.")
    return float(data["High"].iloc[-1]), float(data["Low"].iloc[-1])


def get_current_price(ticker: str) -> float:
    """Get current price for a ticker."""
    try:
        # Use explicit auto_adjust parameter
        data = yf.download(
            ticker,
            period="1d",
            progress=False,
            auto_adjust=True,
        )

        if data.empty:
            # Keep previous behaviour: return None without logging
            return None

        # Use recommended iloc syntax
        close_price = data["Close"].iloc[0]
        return float(close_price)

    except Exception as e:
        msg = f"Error getting price for {ticker}: {e}"
        log_error(msg)
        _register_provider_issue(msg)
        return None
