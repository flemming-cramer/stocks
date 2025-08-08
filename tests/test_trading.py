import pytest
import pandas as pd
from services.trading import execute_buy, execute_sell, validate_trade

@pytest.fixture
def mock_portfolio():
    return pd.DataFrame({
        'Ticker': ['AAPL'],
        'Shares': [10],
        'Price': [150.0]
    })

def test_execute_buy():
    """Test buy execution."""
    trade_data = {
        'ticker': 'MSFT',
        'shares': 5,
        'price': 200.0
    }
    initial_cash = 2000.0
    st.session_state.cash = initial_cash
    
    result = execute_buy(trade_data)
    assert result is True
    assert st.session_state.cash == initial_cash - (trade_data['shares'] * trade_data['price'])

def test_execute_sell():
    """Test sell execution."""
    trade_data = {
        'ticker': 'AAPL',
        'shares': 5,
        'price': 160.0
    }
    initial_cash = 2000.0
    st.session_state.cash = initial_cash
    
    result = execute_sell(trade_data)
    assert result is True
    assert st.session_state.cash == initial_cash + (trade_data['shares'] * trade_data['price'])