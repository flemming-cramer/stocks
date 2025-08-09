import pandas as pd
import yfinance as yf
import streamlit as st

from services.logging import log_error


@st.cache_data(ttl=300)
def fetch_price(ticker: str) -> float | None:
    """Return the latest close price for ``ticker`` or ``None`` on failure."""

    try:  # pragma: no cover - network errors
        data = yf.download(ticker, period="1d", progress=False)
        return float(data["Close"].iloc[-1]) if not data.empty else None
    except Exception:
        log_error(f"Failed to fetch price for {ticker}")
        return None


@st.cache_data(ttl=300)
def fetch_prices(tickers: list[str]) -> pd.DataFrame:
    """Return daily data for ``tickers`` in a single request."""

    if not tickers:
        return pd.DataFrame()

    try:  # pragma: no cover - network errors
        return yf.download(tickers, period="1d", progress=False)
    except Exception:
        log_error(f"Failed to fetch prices for {', '.join(tickers)}")
        return pd.DataFrame()


def get_day_high_low(ticker: str) -> tuple[float, float]:
    """Return today's high and low price for ``ticker``."""

    try:
        data = yf.download(ticker, period="1d", progress=False)
    except Exception as exc:  # pragma: no cover - network errors
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
            auto_adjust=True
        )
        
        if data.empty:
            return None
            
        # Use recommended iloc syntax
        close_price = data["Close"].iloc[0]
        return float(close_price)
        
    except Exception as e:
        logger.error(f"Error getting price for {ticker}: {e}")
        return None
