import pandas as pd
import numpy as np
import pytest
import streamlit as st

import services.watchlist_service as watchlist
from ui.watchlist import add_to_watchlist, remove_from_watchlist


def _clear_cache():
    try:
        watchlist.load_watchlist_prices.clear()
    except Exception:
        pass


def test_load_watchlist_prices_mixed_valid_invalid(monkeypatch):
    calls = {}

    def fake_fetch_prices(tickers):
        calls["tickers"] = tickers
        data = pd.DataFrame(
            {
                ("Close", "GOOD"): [101.0],
                ("Close", "NAN"): [np.nan],
                ("Close", "STR"): ["oops"],
            }
        )
        data.columns = pd.MultiIndex.from_tuples(data.columns)
        return data

    monkeypatch.setattr(watchlist, "fetch_prices", fake_fetch_prices)
    _clear_cache()
    result = watchlist.load_watchlist_prices(["GOOD", "NAN", "STR", "MISS"])
    assert calls["tickers"] == ["GOOD", "NAN", "STR", "MISS"]
    assert result == {"GOOD": 101.0}
    assert all(isinstance(v, float) for v in result.values())


def test_load_watchlist_prices_empty_dataframe(monkeypatch):
    def fake_fetch_prices(tickers):
        return pd.DataFrame()

    monkeypatch.setattr(watchlist, "fetch_prices", fake_fetch_prices)
    _clear_cache()
    result = watchlist.load_watchlist_prices(["ANY"])
    assert result == {}


@pytest.fixture(autouse=True)
def mock_session_state():
    """Setup clean session state before each test."""
    st.session_state.watchlist = []
    st.session_state.watchlist_prices = {}
    st.session_state.watchlist_feedback = None
    return st.session_state


def test_add_to_watchlist(mock_session_state):
    """Test adding ticker to watchlist."""
    add_to_watchlist("AAPL")
    assert len(st.session_state.watchlist) == 1
    assert "AAPL" in st.session_state.watchlist
    assert st.session_state.watchlist_feedback[0] == "success"


def test_add_duplicate_to_watchlist(mock_session_state):
    """Test adding duplicate ticker to watchlist."""
    add_to_watchlist("AAPL")
    add_to_watchlist("AAPL")
    assert st.session_state.watchlist.count("AAPL") == 1
    assert st.session_state.watchlist_feedback[0] == "info"


def test_remove_from_watchlist(mock_session_state):
    """Test removing ticker from watchlist."""
    add_to_watchlist("AAPL")
    remove_from_watchlist("AAPL")
    assert "AAPL" not in st.session_state.watchlist
    assert len(st.session_state.watchlist) == 0


def test_remove_nonexistent_from_watchlist(mock_session_state):
    """Test removing non-existent ticker from watchlist."""
    remove_from_watchlist("INVALID")
    assert len(st.session_state.watchlist) == 0
