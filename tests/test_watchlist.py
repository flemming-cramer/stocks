import pandas as pd
import numpy as np

import services.watchlist_service as watchlist


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
