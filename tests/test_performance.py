import pytest
import pandas as pd
import numpy as np
from pages.performance_page import calculate_kpis, highlight_stop, load_portfolio_history

def test_calculate_kpis_empty_data():
    """Test KPI calculations with empty dataset."""
    empty_df = pd.DataFrame(columns=['ticker', 'total_equity', 'date'])
    kpis = calculate_kpis(empty_df)
    
    assert kpis['initial_equity'] == 0.0
    assert kpis['final_equity'] == 0.0
    assert kpis['net_profit'] == 0.0
    assert kpis['total_return'] == 0.0

def test_calculate_kpis_with_data():
    """Test KPI calculations with sample data."""
    data = {
        'date': pd.date_range(start='2025-01-01', periods=3),
        'ticker': ['TOTAL'] * 3,
        'total_equity': [100.0, 110.0, 105.0]
    }
    df = pd.DataFrame(data)
    kpis = calculate_kpis(df)
    
    assert kpis['initial_equity'] == 100.0
    assert kpis['final_equity'] == 105.0
    assert kpis['net_profit'] == 5.0
    assert kpis['total_return'] == pytest.approx(5.0)

def test_calculate_kpis_with_zero_equity():
    """Test KPI calculations with zero initial equity."""
    data = {
        'date': pd.date_range(start='2025-01-01', periods=2),
        'ticker': ['TOTAL'] * 2,
        'total_equity': [0.0, 100.0]
    }
    df = pd.DataFrame(data)
    kpis = calculate_kpis(df)
    assert kpis['total_return'] == 0.0  # Should handle division by zero

def test_calculate_kpis_with_missing_data():
    """Test KPI calculations with missing data."""
    data = {
        'date': pd.date_range(start='2025-01-01', periods=3),
        'ticker': ['TOTAL'] * 3,
        'total_equity': [100.0, None, 150.0]
    }
    df = pd.DataFrame(data)
    kpis = calculate_kpis(df)
    assert not pd.isna(kpis['total_return'])

def test_highlight_stop():
    """Test stop loss highlighting logic."""
    row_breach = pd.Series({
        'Current Price': 95.0,
        'Stop Loss': 100.0
    })
    row_ok = pd.Series({
        'Current Price': 105.0,
        'Stop Loss': 100.0
    })
    
    assert all(s == 'background-color: #ffcdd2' for s in highlight_stop(row_breach))
    assert all(s == '' for s in highlight_stop(row_ok))