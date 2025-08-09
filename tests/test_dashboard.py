import pytest
import pandas as pd
from unittest.mock import patch
from ui.dashboard import (
    show_portfolio_summary,
    show_holdings_table,
    show_performance_metrics,
    highlight_stop,
    highlight_pct,
    color_pnl,
    render_dashboard  # Add this import
)
from tests.mock_streamlit import StreamlitMock

class MockSessionState(dict):
    """Mock class for Streamlit session state"""
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.portfolio = pd.DataFrame()
        self.cash = 10000.0
        self.__dict__.update(kwargs)

class MockColumn:
    """Simple mock for Streamlit columns"""
    def __init__(self):
        self.calls = []
    
    def __enter__(self):
        return self
    
    def __exit__(self, *args):
        return None
    
    def metric(self, label, value, delta=None):
        self.calls.append(('metric', label, value, delta))

class MockSt:
    """Simple mock for Streamlit"""
    def __init__(self):
        self.session_state = MockSessionState()
        self._columns = [MockColumn(), MockColumn(), MockColumn()]
        self.calls = []
    
    def columns(self, num_cols):
        return self._columns[:num_cols]
    
    def metric(self, label, value, delta=None):
        self.calls.append(('metric', label, value, delta))
    
    def info(self, text):
        self.calls.append(('info', text))
    
    def dataframe(self, df):
        self.calls.append(('dataframe', df))
    
    def subheader(self, text):
        self.calls.append(('subheader', text))
        
    def form(self, key, clear_on_submit=False):
        self.calls.append(('form', key, clear_on_submit))
        return self
    
    def expander(self, label, expanded=False):
        self.calls.append(('expander', label, expanded))
        return self
    
    @property
    def called(self):
        """Check if any calls were made"""
        return len(self.calls) > 0
    
    def assert_called_once_with(self, *args):
        """Assert method was called once with specific args"""
        matching_calls = [c for c in self.calls if c[1:] == args]
        return len(matching_calls) == 1
    
    def assert_called_with(self, *args):
        """Assert method was called with specific args"""
        return any(c[1:] == args for c in self.calls)

@pytest.fixture
def mock_portfolio_data():
    """Create sample portfolio data."""
    return pd.DataFrame({
        'ticker': ['AAPL', 'MSFT'],
        'shares': [100, 50],
        'price': [150.0, 200.0],
        'buy_price': [140.0, 190.0],
        'cost_basis': [14000.0, 9500.0],
        'market_value': [15000.0, 10000.0],
        'stop_loss': [135.0, 180.0],
        'Return %': [7.14, 5.26]  # Added for highlight_pct test
    })

@pytest.fixture
def mock_streamlit():
    """Create streamlit mock with session state."""
    return StreamlitMock()

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
    assert 'color: green' in result[0]  # Positive return
    assert 'color: green' in result[1]  # Positive return

def test_show_portfolio_summary(mock_streamlit, mock_portfolio_data):
    """Test portfolio summary display."""
    with patch('ui.dashboard.st', mock_streamlit):
        mock_streamlit.session_state.portfolio = mock_portfolio_data
        show_portfolio_summary()
        assert mock_streamlit.assert_called('metric')

def test_show_holdings_table_empty(mock_streamlit):
    """Test holdings table with empty portfolio."""
    with patch('ui.dashboard.st', mock_streamlit):
        show_holdings_table()
        assert mock_streamlit.assert_info_called_with("No holdings to display")

def test_show_holdings_table_with_data(mock_streamlit, mock_portfolio_data):
    """Test holdings table with data."""
    with patch('ui.dashboard.st', mock_streamlit):
        mock_streamlit.session_state.portfolio = mock_portfolio_data
        show_holdings_table()
        assert any(call[0] == 'dataframe' for call in mock_streamlit.calls)

def test_show_performance_metrics(mock_streamlit):
    """Test performance metrics display."""
    metrics = {
        'total_value': 25000.0,
        'total_gain': 5000.0,
        'total_return': 0.25
    }
    
    with patch('ui.dashboard.st', mock_streamlit):
        show_performance_metrics(metrics)
        assert mock_streamlit.assert_called('metric')
        assert len(mock_streamlit.get_calls('metric')) == 3

def test_render_dashboard_empty_portfolio(mock_streamlit):
    """Test dashboard rendering with empty portfolio."""
    with patch('ui.dashboard.st', mock_streamlit):
        render_dashboard()
        assert mock_streamlit.assert_called_with(
            'info', 
            "Your portfolio is empty. Use the Buy form below to add your first position."
        )

def test_render_dashboard_with_data(mock_streamlit, mock_portfolio_data):
    """Test dashboard rendering with portfolio data."""
    with patch('ui.dashboard.st', mock_streamlit):
        mock_streamlit.session_state.portfolio = mock_portfolio_data
        render_dashboard()
        assert mock_streamlit.assert_called('dataframe')