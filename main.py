# src/forexfactory/main.py

import sys
import os
import logging
import argparse
from datetime import datetime
from dateutil.tz import gettz

from src.incremental import scrape_incremental


start = '2023-01-01'
cycles = 6
timezone = 'Asia/Tehran'


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

if __name__ == "__main__":
    main()