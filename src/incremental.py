import logging

from .scraper import scrape_range_pandas

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s [%(levelname)s] %(name)s: %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)
logger = logging.getLogger(__name__)

def scrape_incremental(from_date, cycles, tzname="Asia/Tehran"):
    """
    Example: day-by-day approach but we only re-scrape if day is missing or incomplete.
    For simplicity, let's re-scrape entire range. Then we can add logic if needed.
    """
    # You can implement a logic that checks existing_df if days are complete or not.
    # For now, let's just call scrape_range_pandas:
    scrape_range_pandas(from_date, cycles, tzname=tzname)
