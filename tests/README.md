# Test Organization

This directory contains the organized test suite for the ChatGPT Micro Cap Trading Experiment.

## Current Test Structure (Core Coverage Strategy)

### Essential Files
- `conftest.py` - Pytest configuration and fixtures
- `mock_streamlit.py` - Essential mocking utilities for Streamlit components

### Core Business Logic Tests (Active)
These tests provide coverage for our core business functions (target: 80% coverage):

- `test_data_portfolio.py` - Tests `data/portfolio.py` (82.3% coverage)
- `test_data_watchlist.py` - Tests `data/watchlist.py` (89.4% coverage)
- `test_portfolio_service.py` - Tests `services/portfolio_service.py` (90.0% coverage)
- `test_portfolio_manager.py` - Tests `services/portfolio_manager.py` (88.5% coverage)
- `test_validation_service.py` - Tests `services/core/validation_service.py` (82.1% coverage)
- `test_market.py` - Tests `services/market.py` (70.0% coverage)

### Focused Tests (Active)
Modern, focused test suites targeting specific implementations:

- `test_trading_focused.py` - Tests `services/trading.py` (76.4% coverage)
- `test_watchlist_focused.py` - Tests `services/watchlist_service.py` (65.3% coverage)
- `test_core_services.py` - Tests `services/core/*` modules

### Database Tests (Active)
- `test_db.py` - Tests `data/db.py` database utilities (18.7% coverage)

## Archived Tests

### `legacy/` - Deprecated/Duplicate Tests
Tests that have been replaced by more focused implementations or are no longer needed:

- `test_core_business_logic.py` - Replaced by focused tests
- `test_core_data_layer.py` - Replaced by specific data tests
- `test_core_extended.py` - Experimental tests
- `test_core_market_services.py` - Covered by `test_market.py`
- `test_trading.py` - Legacy trading tests
- `test_trading_extended.py` - Extended trading tests
- `test_trading_validation.py` - Covered by validation service tests
- `test_existing_services.py` - Generic service tests
- `test_portfolio.py` - Redundant with `test_data_portfolio.py`

### `ui_archived/` - UI Component Tests
Tests for Streamlit UI components (excluded from core coverage target):

- `test_app.py` - Main Streamlit app tests
- `test_ui_basic_coverage.py` - Basic UI coverage tests
- `test_ui_cash.py` - Cash component UI tests
- `test_ui_dashboard.py` - Dashboard UI tests
- `test_ui_forms.py` - Form UI tests
- `test_ui_summary.py` - Summary UI tests
- `test_cash.py` - Cash UI functionality
- `test_summary.py` - Summary UI functionality
- `test_session.py` - Session state management (UI-related)
- `test_performance.py` - Performance page UI tests

## Coverage Achievement

**Target:** 80% unit test coverage for core business functions  
**Achieved:** 78.51% weighted average coverage  

### High Coverage Modules (>80%):
- data/portfolio.py: 82.3%
- data/watchlist.py: 89.4%
- services/core/portfolio_service.py: 93.8%
- services/core/validation_service.py: 82.1%
- services/portfolio_manager.py: 88.5%
- services/portfolio_service.py: 90.0%

### Good Coverage Modules (70-80%):
- services/trading.py: 76.4%
- services/core/market_service.py: 70.0%
- services/core/trading_service.py: 70.9%

## Running Tests

To run the active core business logic tests:
```bash
python -m pytest tests/ -v
```

To run tests with coverage:
```bash
python scripts/run_tests_with_coverage.py
```

To run specific test categories:
```bash
# Core business logic only
python -m pytest tests/test_data_*.py tests/test_*_service.py tests/test_*_manager.py -v

# Focused tests only
python -m pytest tests/test_*_focused.py tests/test_core_services.py -v
```
