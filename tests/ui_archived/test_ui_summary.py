"""Tests for ui/summary.py module."""

import pytest
import pandas as pd
from unittest.mock import patch
import sys
from pathlib import Path

# Add project root to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from ui.summary import build_daily_summary


class TestBuildDailySummary:
    """Test the build_daily_summary function."""
    
    def test_empty_portfolio(self):
        """Test summary with empty portfolio."""
        empty_df = pd.DataFrame()
        
        result = build_daily_summary(empty_df)
        
        assert result == "No portfolio data available for summary."
    
    def test_missing_required_columns(self):
        """Test summary with missing required columns."""
        # Create DataFrame with missing columns
        incomplete_df = pd.DataFrame({
            'Ticker': ['AAPL'],
            'Shares': [100],
            # Missing 'Cost Basis', 'Current Price', 'Total Value'
        })
        
        result = build_daily_summary(incomplete_df)
        
        assert "Error generating summary: Missing required columns" in result
    
    def test_valid_portfolio_with_cash(self):
        """Test summary with valid portfolio data including cash."""
        portfolio_df = pd.DataFrame({
            'Ticker': ['AAPL', 'MSFT'],  # Only actual positions
            'Shares': [100, 50],
            'Cost Basis': [150.0, 300.0],
            'Current Price': [160.0, 320.0],
            'Total Value': [16000.0, 16000.0],  # Only values for actual positions
            'Cash Balance': [5000.0, '']  # Only first row has cash
        })
        
        result = build_daily_summary(portfolio_df)
        
        assert "Portfolio Summary" in result
        assert "Total Value: $32,000.00" in result  # Sum of actual position values
        assert "Cash Balance: $5,000.00" in result
        assert "Total Equity: $37,000.00" in result
        assert "Positions: 2" in result  # AAPL, MSFT
    
    def test_valid_portfolio_no_cash_column(self):
        """Test summary with valid portfolio but no cash balance column."""
        portfolio_df = pd.DataFrame({
            'Ticker': ['AAPL', 'MSFT'],
            'Shares': [100, 50],
            'Cost Basis': [150.0, 300.0],
            'Current Price': [160.0, 320.0],
            'Total Value': [16000.0, 16000.0]
        })
        
        result = build_daily_summary(portfolio_df)
        
        assert "Portfolio Summary" in result
        assert "Total Value: $32,000.00" in result
        assert "Cash Balance: $0.00" in result
        assert "Total Equity: $32,000.00" in result
        assert "Positions: 2" in result
    
    def test_portfolio_with_zero_values(self):
        """Test summary with zero values."""
        portfolio_df = pd.DataFrame({
            'Ticker': ['AAPL'],
            'Shares': [0],
            'Cost Basis': [0.0],
            'Current Price': [0.0],
            'Total Value': [0.0],
            'Cash Balance': [0.0]
        })
        
        result = build_daily_summary(portfolio_df)
        
        assert "Total Value: $0.00" in result
        assert "Cash Balance: $0.00" in result
        assert "Total Equity: $0.00" in result
        assert "Positions: 1" in result
    
    def test_portfolio_with_single_position(self):
        """Test summary with single position."""
        portfolio_df = pd.DataFrame({
            'Ticker': ['AAPL'],
            'Shares': [100],
            'Cost Basis': [150.0],
            'Current Price': [160.0],
            'Total Value': [16000.0],
            'Cash Balance': [2000.0]
        })
        
        result = build_daily_summary(portfolio_df)
        
        assert "Total Value: $16,000.00" in result
        assert "Cash Balance: $2,000.00" in result
        assert "Total Equity: $18,000.00" in result
        assert "Positions: 1" in result
    
    def test_portfolio_with_large_numbers(self):
        """Test summary with large monetary values."""
        portfolio_df = pd.DataFrame({
            'Ticker': ['AAPL', 'MSFT'],
            'Shares': [1000, 500],
            'Cost Basis': [150.0, 300.0],
            'Current Price': [160.0, 320.0],
            'Total Value': [160000.0, 160000.0],
            'Cash Balance': [50000.0, '']
        })
        
        result = build_daily_summary(portfolio_df)
        
        assert "Total Value: $320,000.00" in result
        assert "Cash Balance: $50,000.00" in result
        assert "Total Equity: $370,000.00" in result
    
    def test_exception_handling(self):
        """Test that exceptions are properly handled."""
        # Create a DataFrame that might cause issues
        problematic_df = pd.DataFrame({
            'Ticker': ['AAPL'],
            'Shares': ['invalid'],  # Non-numeric value
            'Cost Basis': [150.0],
            'Current Price': [160.0],
            'Total Value': ['also_invalid'],
            'Cash Balance': [2000.0]
        })
        
        result = build_daily_summary(problematic_df)
        
        assert "Error generating summary:" in result
    
    def test_portfolio_summary_format(self):
        """Test that the summary format is correct."""
        portfolio_df = pd.DataFrame({
            'Ticker': ['AAPL'],
            'Shares': [100],
            'Cost Basis': [150.0],
            'Current Price': [160.0],
            'Total Value': [16000.0],
            'Cash Balance': [2000.0]
        })
        
        result = build_daily_summary(portfolio_df)
        lines = result.split('\n')
        
        assert lines[0] == "Portfolio Summary"
        assert lines[1] == "-" * 20
        assert "Total Value:" in lines[2]
        assert "Cash Balance:" in lines[3]
        assert "Total Equity:" in lines[4]
        assert "Positions:" in lines[5]
    
    def test_unique_tickers_count(self):
        """Test that unique ticker count is correct even with duplicates."""
        portfolio_df = pd.DataFrame({
            'Ticker': ['AAPL', 'AAPL', 'MSFT'],  # AAPL appears twice
            'Shares': [50, 50, 100],
            'Cost Basis': [150.0, 155.0, 300.0],
            'Current Price': [160.0, 160.0, 320.0],
            'Total Value': [8000.0, 8000.0, 32000.0],
            'Cash Balance': [1000.0, '', '']
        })
        
        result = build_daily_summary(portfolio_df)
        
        # Should count unique tickers only
        assert "Positions: 2" in result  # AAPL and MSFT
