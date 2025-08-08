import pytest
import pandas as pd
from unittest.mock import patch, MagicMock
from ui.dashboard import (
    show_portfolio_summary,
    show_holdings_table,
    show_performance_metrics,
    highlight_stop,
    highlight_pct,
    color_pnl,
    render_dashboard  # Add this import
)

@pytest.fixture
def mock_portfolio_data():
    """Create sample portfolio data."""
    return pd.DataFrame({
        'Ticker': ['AAPL', 'MSFT'],
        'Shares': [100, 50],
        'Current Price': [150.0, 200.0],
        'Stop Loss': [140.0, 170.0],
        'Market Value': [15000.0, 10000.0],
        'Cost Basis': [14000.0, 9500.0],
        'Return %': [7.14, -5.0]
    })

@pytest.fixture
def mock_streamlit():
    """Create streamlit mock."""
    mock_st = MagicMock()
    mock_st.session_state = MagicMock()
    mock_st.session_state.portfolio = pd.DataFrame()
    mock_st.columns.return_value = [MagicMock(), MagicMock(), MagicMock()]
    return mock_st

def test_color_pnl():
    """Test P&L coloring."""
    assert color_pnl(100) == 'color: green'
    assert color_pnl(-100) == 'color: red'
    assert color_pnl(0) == ''
    assert color_pnl('invalid') == ''

def test_highlight_stop(mock_portfolio_data):
    """Test stop loss highlighting."""
    result = highlight_stop(mock_portfolio_data.iloc[0])
    assert isinstance(result, list)
    assert all(isinstance(x, str) for x in result)

def test_highlight_pct(mock_portfolio_data):
    """Test percentage highlighting."""
    result = highlight_pct(mock_portfolio_data['Return %'])
    assert isinstance(result, list)
    assert 'color: green' in result
    assert 'color: red' in result

def test_show_portfolio_summary(mock_streamlit, mock_portfolio_data):
    """Test portfolio summary display."""
    with patch('ui.dashboard.st', mock_streamlit):
        mock_streamlit.session_state.portfolio = mock_portfolio_data
        show_portfolio_summary()
        
        # Verify metrics were displayed
        mock_streamlit.columns.assert_called_once_with(3)
        cols = mock_streamlit.columns.return_value
        
        # Check metric calls on each column
        for col in cols:
            assert col.metric.called

def test_show_holdings_table_empty(mock_streamlit):
    """Test holdings table with empty portfolio."""
    with patch('ui.dashboard.st', mock_streamlit):
        show_holdings_table()
        mock_streamlit.info.assert_called_once_with("No holdings to display")

def test_show_holdings_table_with_data(mock_streamlit, mock_portfolio_data):
    """Test holdings table with data."""
    with patch('ui.dashboard.st', mock_streamlit) as mocked_st:
        # Set up portfolio data
        mocked_st.session_state.portfolio = mock_portfolio_data
        
        # Call the function
        show_holdings_table()
        
        # Verify dataframe was called with formatted data
        called_args = mocked_st.dataframe.call_args
        assert called_args is not None, "dataframe() was not called"
        df_arg = called_args[0][0]  # Get the first positional argument
        assert isinstance(df_arg, pd.DataFrame), "Argument is not a DataFrame"

def test_show_performance_metrics(mock_streamlit):
    """Test performance metrics display."""
    metrics = {
        'total_value': 5500.0,
        'total_gain': 250.0,
        'total_return': 0.0476
    }
    with patch('ui.dashboard.st', mock_streamlit):
        show_performance_metrics(metrics)
        assert mock_streamlit.columns.called

def test_render_dashboard_empty_portfolio(mock_streamlit):
    """Test dashboard rendering with empty portfolio."""
    with patch('ui.dashboard.st', mock_streamlit):
        render_dashboard()
        mock_streamlit.info.assert_called_once_with(
            "Your portfolio is empty. Use the Buy form below to add your first position."
        )

def test_render_dashboard_with_data(mock_streamlit, mock_portfolio_data):
    """Test dashboard rendering with portfolio data."""
    with patch('ui.dashboard.st', mock_streamlit):
        mock_streamlit.session_state.portfolio = mock_portfolio_data
        render_dashboard()
        mock_streamlit.subheader.assert_called_with("Current Holdings")