import json
import logging

from config import WATCHLIST_FILE


logger = logging.getLogger(__name__)


def load_watchlist() -> list[str]:
    """Return saved watchlist tickers from ``WATCHLIST_FILE``."""

    if WATCHLIST_FILE.exists():
        try:
            data = json.loads(WATCHLIST_FILE.read_text())
            return [str(t).upper() for t in data if isinstance(t, str)]
        except Exception:
            logger.exception("Failed to load watchlist")
    return []


def save_watchlist(tickers: list[str]) -> None:
    """Persist ``tickers`` to ``WATCHLIST_FILE`` as JSON."""

    try:
        WATCHLIST_FILE.write_text(json.dumps(tickers))
    except Exception:
        logger.exception("Failed to save watchlist")
