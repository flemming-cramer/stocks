"""Tests for ui/cash.py module."""

import pytest
from unittest.mock import patch, MagicMock
import sys
from pathlib import Path

# Add project root to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from ui.cash import show_cash_section


class TestCashSection:
    """Test the cash section UI functionality."""
    
    @patch('ui.cash.save_portfolio_snapshot')
    @patch('ui.cash.st')
    def test_show_cash_section_display(self, mock_st, mock_save):
        """Test basic cash section display."""
        # Mock session state
        mock_st.session_state.cash = 10000.50
        mock_st.session_state.__contains__ = MagicMock(return_value=True)
        mock_st.session_state.show_cash_form = False
        mock_st.button.return_value = False
        
        show_cash_section()
        
        # Verify subheader was called
        mock_st.subheader.assert_called_once_with("Cash Balance")
        
        # Verify metric was called with formatted cash value
        mock_st.metric.assert_called_once_with(
            label="Available Cash",
            value="$10,000.50"
        )
        
        # Verify button was created (with type parameter)
        mock_st.button.assert_called_once_with("Add Cash", key="toggle_cash", type="primary")
    
    @patch('ui.cash.save_portfolio_snapshot')
    @patch('ui.cash.st')
    def test_cash_formatting(self, mock_st, mock_save):
        """Test cash value formatting for different amounts."""
        test_cases = [
            (0.0, "$0.00"),
            (1234.56, "$1,234.56"),
            (1000000.99, "$1,000,000.99"),
            (0.01, "$0.01")
        ]
        
        for cash_amount, expected_format in test_cases:
            mock_st.reset_mock()
            mock_st.session_state.cash = cash_amount
            mock_st.session_state.__contains__ = MagicMock(return_value=True)
            mock_st.session_state.show_cash_form = False
            mock_st.button.return_value = False
            
            show_cash_section()
            
            mock_st.metric.assert_called_once_with(
                label="Available Cash",
                value=expected_format
            )
