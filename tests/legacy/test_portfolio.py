import pytest
import pandas as pd
from portfolio import ensure_schema, PORTFOLIO_COLUMNS
from services.portfolio_service import update_portfolio


def test_ensure_schema_adds_missing_columns():
    df = pd.DataFrame({"ticker": ["ABC"], "shares": [10]})
    result = ensure_schema(df)
    assert list(result.columns) == PORTFOLIO_COLUMNS
    # Missing numeric columns should default to 0
    assert result.loc[0, "stop_loss"] == 0


def test_update_portfolio():
    """Test portfolio update with timestamp."""
    transaction = {
        'ticker': 'AAPL',
        'shares': 10,
        'price': 150.0
    }

    result = update_portfolio(transaction)
    assert 'timestamp' in result
    assert isinstance(result['timestamp'], pd.Timestamp)


def test_update_portfolio_validates_data():
    """Test portfolio update with invalid data."""
    transaction = {'ticker': 'INVALID'}  # Missing required fields
    with pytest.raises(ValueError):
        update_portfolio(transaction)


def test_update_portfolio_with_empty_data():
    """Test portfolio update with empty transaction."""
    with pytest.raises(ValueError):
        update_portfolio({})
