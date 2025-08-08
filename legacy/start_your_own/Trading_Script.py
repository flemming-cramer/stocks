# Improved user prompts and guidance for manual trades and daily summaries
# (2025-08-04 usability update)
"""Wrapper for the shared trading script using a local data directory.

This example script is archived and kept for reference only.
"""

from pathlib import Path

from trading_script import main


if __name__ == "__main__":

    data_dir = Path(__file__).resolve().parent
    main("Start Your Own/chatgpt_portfolio_update.csv", Path("Start Your Own"))

