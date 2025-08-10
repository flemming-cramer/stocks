import pytest
import pandas as pd
from ui.summary import build_daily_summary

@pytest.fixture
def mock_portfolio_data():
    """Create sample portfolio data."""
    return pd.DataFrame({
        'Ticker': ['AAPL', 'MSFT'],
        'Shares': [100, 50],
        'Cost Basis': [15000.0, 10000.0],
        'Current Price': [155.0, 205.0],
        'Total Value': [15500.0, 10250.0],
        'Cash Balance': [5000.0, 5000.0]
    })

def test_build_daily_summary_with_data(mock_portfolio_data):
    """Test daily summary generation with portfolio data."""
    summary = build_daily_summary(mock_portfolio_data)
    
    # Verify summary contains expected sections
    assert "Portfolio Summary" in summary
    assert "Total Value: $25,750.00" in summary
    assert "Cash Balance: $5,000.00" in summary
    assert "Total Equity: $30,750.00" in summary
    assert "Positions: 2" in summary

def test_build_daily_summary_empty():
    """Test daily summary generation with empty portfolio."""
    empty_df = pd.DataFrame(columns=['Ticker', 'Shares', 'Cost Basis', 'Current Price', 'Total Value'])
    summary = build_daily_summary(empty_df)
    assert summary == "No portfolio data available for summary."

def test_build_daily_summary_missing_columns():
    """Test daily summary generation with missing columns."""
    incomplete_df = pd.DataFrame({
        'Ticker': ['AAPL'],
        'Shares': [100]
    })
    summary = build_daily_summary(incomplete_df)
    assert "Error generating summary: Missing required columns" in summary