"""Wrapper for the shared trading script using a legacy data directory.

This file is retained for historical reference and is no longer maintained.
"""

from pathlib import Path

from trading_script import main


if __name__ == "__main__":

    data_dir = Path(__file__).resolve().parent
    main("Scripts and CSV Files/chatgpt_portfolio_update.csv", Path("Scripts and CSV Files"))


