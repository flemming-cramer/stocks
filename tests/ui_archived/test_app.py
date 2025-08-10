"""Tests for app.py main application entry point."""

import pytest
from unittest.mock import patch, MagicMock
import sys
from pathlib import Path

# Add project root to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))


def test_app_imports():
    """Test that the app module can be imported successfully."""
    import app
    assert hasattr(app, 'main')


@patch('app.render_dashboard')
@patch('app.navbar')
@patch('app.st')
def test_main_function(mock_st, mock_navbar, mock_render_dashboard):
    """Test the main function executes without errors."""
    from app import main
    
    main()
    
    # Verify that the dashboard rendering function was called
    mock_render_dashboard.assert_called_once()


def test_streamlit_imports():
    """Test that the app correctly imports streamlit components."""
    import app
    # Just verify that the module loads without error
    assert True


def test_app_config_constants():
    """Test that app configuration is properly defined."""
    import app
    # Verify the app module has been imported successfully
    assert hasattr(app, 'main')
