import pytest
import pandas as pd
import streamlit as st
from unittest.mock import patch
from services.trading import execute_buy, execute_sell

@pytest.fixture(autouse=True)
def mock_session_state():
    """Setup session state before each test."""
    st.session_state.cash = 2000.0
    st.session_state.portfolio = pd.DataFrame(columns=['Ticker', 'Shares', 'Price'])
    return st.session_state

def test_execute_buy(mock_session_state):
    """Test buy execution."""
    with patch('services.trading.st.error', return_value=None):
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

def test_execute_sell(mock_session_state):
    """Test sell execution."""
    with patch('services.trading.st.error', return_value=None):
        # Setup initial portfolio
        st.session_state.portfolio = pd.DataFrame({
            'Ticker': ['AAPL'],
            'Shares': [10],
            'Price': [150.0]
        })
        
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