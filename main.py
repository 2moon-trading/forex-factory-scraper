import logging
from datetime import datetime
from dateutil.tz import gettz # type: ignore

from src.incremental import scrape_incremental


start = '2025-08-10'
cycles = 1
timezone = 'Asia/Tehran'

#2025-08-10 13:23:58 [INFO] undetected_chromedriver.patcher: patching driver executable /Users/santiagogaleanograndeth/Library/Application Support/undetected_chromedriver/undetected_chromedriver

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s [%(levelname)s] %(name)s: %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)
logger = logging.getLogger(__name__)

def main():
    tz = gettz(timezone)
    from_date = datetime.fromisoformat(start).replace(tzinfo=tz)

    scrape_incremental(from_date, cycles, tzname=timezone)

main()