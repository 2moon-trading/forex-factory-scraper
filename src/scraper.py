import copy
import datetime as dt
from datetime import datetime
import re
import logging
import pandas as pd # type: ignore
from selenium.webdriver.common.by import By # type: ignore
from selenium.webdriver.support.ui import WebDriverWait # type: ignore
from selenium.webdriver.support import expected_conditions as EC # type: ignore
from selenium.common.exceptions import ( # type: ignore
    NoSuchElementException,
    TimeoutException,
)
import undetected_chromedriver as uc # type: ignore

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s [%(levelname)s] %(name)s: %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)
logger = logging.getLogger(__name__)

COLUMNS = [
    "Week", "Date", "Time", "Currency", "Impact", "Event", "Actual", "Forecast", "Previous"
]


def parse_calendar_day(driver, week: dt.datetime, the_date: dt.datetime) -> pd.DataFrame:
    """
    Scrape data for a single day (the_date) and return a DataFrame with columns:
    -DateTime, Currency, Impact, Event, Actual, Forecast, Previous, Detail
    If scrape_details is False, skip detail parsing.

    Before fetching detail data from the Internet, this function checks if the record
    already exists (using existing_df) with a non-empty "Detail" field.
    """
    date_str = the_date.strftime('%b%d.%Y').lower()
    url = f"https://www.forexfactory.com/calendar?day={date_str}"
    logger.info(f"Scraping URL: {url}")
    driver.get(url)

    try:
        WebDriverWait(driver, 15).until(
            EC.visibility_of_element_located((By.XPATH, '//table[contains(@class,"calendar__table")]'))
        )
    except TimeoutException:
        logger.warning(f"Page did not load for day={the_date.date()}")
        return pd.DataFrame(columns=COLUMNS)

    rows = driver.find_elements(By.XPATH, '//tr[contains(@class,"calendar__row")]')
    data_list = []
    current_day = the_date

    logger.info(f"Found {len(rows)} rows for {current_day.date()}")

    for row in rows:
        row_class = row.get_attribute("class")
        if "day-breaker" in row_class or "no-event" in row_class:
            continue

        # Parse the basic cells
        try:
            date_el = row.find_element(By.XPATH, './/td[contains(@class,"calendar__date")]')
            date_text = date_el.text.strip()
        except NoSuchElementException:
            date_text = ""

        try:
            time_el = row.find_element(By.XPATH, './/td[contains(@class,"calendar__time")]')
            time_text = time_el.text.strip()
        except NoSuchElementException:
            time_text = ""

        try:
            currency_el = row.find_element(By.XPATH, './/td[contains(@class,"calendar__currency")]')
            currency_text = currency_el.text.strip()
        except NoSuchElementException:
            currency_text = ""

        impact_text = ""
        try:
            impact_el = row.find_element(By.XPATH, './/td[contains(@class,"calendar__impact")]')
            impact_text = ""
            try:
                impact_span = impact_el.find_element(By.XPATH, './/span')
                impact_text = impact_span.get_attribute("title") or ""
            except Exception:
                impact_text = impact_el.text.strip()
        except NoSuchElementException:
            pass

        try:
            event_el = row.find_element(By.XPATH, './/td[contains(@class,"calendar__event")]')
            event_text = event_el.text.strip()
        except NoSuchElementException:
            event_text = ""

        try:
            actual_el = row.find_element(By.XPATH, './/td[contains(@class,"calendar__actual")]')
            actual_text = actual_el.text.strip()
        except NoSuchElementException:
            actual_text = ""

        try:
            forecast_el = row.find_element(By.XPATH, './/td[contains(@class,"calendar__forecast")]')
            forecast_text = forecast_el.text.strip()
        except NoSuchElementException:
            forecast_text = ""

        try:
            previous_el = row.find_element(By.XPATH, './/td[contains(@class,"calendar__previous")]')
            previous_text = previous_el.text.strip()
        except NoSuchElementException:
            previous_text = ""

        # Determine event time based on text
        event_dt = current_day
        time_lower = time_text.lower()
        if "day" in time_lower:
            event_dt = event_dt.replace(hour=23, minute=59, second=59)
        elif "data" in time_lower:
            event_dt = event_dt.replace(hour=0, minute=0, second=1)
        else:
            m = re.match(r'(\d{1,2}):(\d{2})(am|pm)', time_lower)
            if m:
                hh = int(m.group(1))
                mm = int(m.group(2))
                ampm = m.group(3)
                if ampm == 'pm' and hh < 12:
                    hh += 12
                if ampm == 'am' and hh == 12:
                    hh = 0
                event_dt = event_dt.replace(hour=hh, minute=mm, second=0)

        if time_text != "All Day" and time_text != "":
            time_text = datetime.strptime(time_text, "%I:%M%p").strftime("%H:%M:%S")

        _the_date = str(the_date.strftime('%Y-%m-%d'))

        event_text = event_text.replace("\n", " ").replace("\\/", "/").replace("mm", "m/m").replace("qq", "q/q").replace("yy", "y/y").strip()

        date_text = date_text.replace("\n", " ").replace("\\", "").strip()

        if date_text == '':
            date_text = next(data['Date'] for data in reversed(data_list) if data['Date'] != '')

        year = _the_date.split("-")[0]
        if year not in date_text:
            date_text = f"{year} {date_text}"

        if len(date_text.split(' ')) > 2:
            date_text = datetime.strptime(date_text, "%Y %a %b %d")
            date_text = date_text.strftime("%Y-%m-%d")

        if actual_text == "":
            actual_text = None
        else:
            actual_text = actual_text if '|' not in actual_text else actual_text.split('|')[0]
            actual_text = float(actual_text.replace("%", "").replace("K", "").replace("M", "").replace("B", "").replace("T", "").strip())

        if forecast_text == "":
            forecast_text = None
        else:
            forecast_text = forecast_text if '|' not in forecast_text else forecast_text.split('|')[0]
            forecast_text = float(forecast_text.replace("%", "").replace("K", "").replace("M", "").replace("B", "").replace("T", "").strip())

        if previous_text == "":
            previous_text = None
        else:
            previous_text = previous_text if '|' not in previous_text else previous_text.split('|')[0]
            previous_text = float(previous_text.replace("%", "").replace("K", "").replace("M", "").replace("B", "").replace("T", "").strip())

        if impact_text == "Non-Economic" or impact_text == "" or impact_text is None:
            impact_text = None
        elif 'Low' in impact_text:
            impact_text = "Low"
        elif 'Medium' in impact_text:
            impact_text = "Medium"
        elif 'High' in impact_text:
            impact_text = "High"
        elif 'Very High' in impact_text:
            impact_text = "Very High"
        else:
            impact_text = "Unknown"

        data_list.append({
            "Week": week.strftime('%Y-%m-%d'),
            "Date": date_text ,
            "Time": time_text,
            "Currency": currency_text,
            "Impact": impact_text,
            "Event": event_text,
            "Actual": actual_text,
            "Forecast": forecast_text,
            "Previous": previous_text,
        })

    return pd.DataFrame(data_list)


def scrape_week(driver, the_date: datetime) -> pd.DataFrame:
    """
    Re-scrape a single day, using existing_df to check for already-saved details.
    """
    week_df = pd.DataFrame(columns=COLUMNS)
    week = the_date
    _cycles = 0
    while _cycles < 7:
        print(week)
        print(the_date)
        logger.info(f"Scraping day {the_date.strftime('%Y-%m-%d')}...")
        df_day_new = parse_calendar_day(driver, week, the_date)
        week_df = pd.concat([week_df, df_day_new], ignore_index=True)
        the_date += dt.timedelta(days=1)
        _cycles += 1
    return week_df


def scrape_range_pandas(from_date: datetime, cycles: int, tzname="Asia/Tehran"):
    driver = uc.Chrome()
    driver.set_window_size(1400, 1000)

    logger.info(f"Scraping {from_date.date()} for {cycles} cycles.")

    _cycles = 0

    df = pd.DataFrame(columns=COLUMNS)

    try:
        current_week = from_date
        while _cycles < cycles:
            logger.info(f"Scraping week {current_week.strftime('%Y-%m-%d')}...")
            df = pd.concat([df, scrape_week(driver, current_week)], ignore_index=True)
            current_week += dt.timedelta(days=7)
            _cycles += 1

        json_str = df.to_json(orient='records', indent=2)
        with open("noticias.json", "w", encoding="utf-8") as f:
            f.write(json_str)

    finally:
        if driver:
            try:
                driver.quit()
                logger.info("Chrome WebDriver closed successfully.")
            except OSError as ose:
                # Ignore specific OSError during final cleanup (e.g., WinError 6)
                logger.debug(f"Ignored OSError during WebDriver quit: {ose}")
            except Exception as e:
                logger.error(f"Error closing WebDriver: {e}")
            finally:
                driver = None

    # Final save (if needed)
    logger.info(f"Done. Total new/updated rows: {len(df)}")
