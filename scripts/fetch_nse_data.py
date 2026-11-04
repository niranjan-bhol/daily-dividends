import csv
import json
import time
import requests
from datetime import date, timedelta
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent
INPUT_PATH = BASE_DIR / "data" / "symbol" / "NIFTY-500-FILTERED-BY-PRICE.csv"
OUTPUT_DIR = BASE_DIR / "data" / "nse" / "raw"
OUTPUT_PATH_DISPLAY = f"{BASE_DIR.name}/{OUTPUT_DIR.relative_to(BASE_DIR)}"

END_DATE = date.today() - timedelta(days=1)
START_DATE = END_DATE - timedelta(days=365)
CHUNK_DAYS = 90
RETRIES = 3
REQUEST_SLEEP = 0.2
SESSION_REFRESH_INTERVAL = 50

BASE_URL = "https://www.nseindia.com"
API_URL = f"{BASE_URL}/api/historicalOR/generateSecurityWiseHistoricalData"

HEADERS = {
    "accept": "*/*",
    "accept-language": "en-GB,en;q=0.7",
    "referer": f"{BASE_URL}/report-detail/eq_security",
    "user-agent": (
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/156.0.0.0 Safari/537.36"
    ),
}

def read_symbols():
    with open(INPUT_PATH, newline="") as f:
        symbols = (row["symbol"].strip() for row in csv.DictReader(f))
        return [s for s in symbols if s]

def prepare_output_dir():
    if OUTPUT_DIR.exists():
        for file in OUTPUT_DIR.glob("*.json"):
            file.unlink()
        print(f"Output directory exists : {OUTPUT_PATH_DISPLAY}")
        print("Cleared output directory")
    else:
        OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
        print(f"Created output directory : {OUTPUT_PATH_DISPLAY}")

def create_session():
    session = requests.Session()
    session.headers.update(HEADERS)
    for attempt in range(RETRIES):
        try:
            session.get(BASE_URL, timeout=10).raise_for_status()
            time.sleep(1)
            return session
        except requests.RequestException:
            time.sleep(2**attempt)
    return None

def date_chunks():
    start = START_DATE
    while start <= END_DATE:
        end = min(start + timedelta(days=CHUNK_DAYS - 1), END_DATE)
        yield start.strftime("%d-%m-%Y"), end.strftime("%d-%m-%Y")
        start = end + timedelta(days=1)

def fetch_symbol(session, symbol):
    records = []
    for from_date, to_date in date_chunks():
        params = {
            "from": from_date,
            "to": to_date,
            "symbol": symbol,
            "type": "priceVolumeDeliverable",
            "series": "ALL",
        }
        response = session.get(API_URL, params=params, timeout=15)
        response.raise_for_status()
        records.extend(response.json()["data"])
        time.sleep(REQUEST_SLEEP)
    return sorted(records, key=lambda r: r["CH_TIMESTAMP"])

def process_symbol(session, symbol, label):
    for attempt in range(RETRIES):
        try:
            records = fetch_symbol(session, symbol)
            with open(OUTPUT_DIR / f"{symbol}.json", "w") as f:
                json.dump({"data": records}, f, indent=2)
        except (requests.RequestException, KeyError, ValueError, OSError):
            time.sleep(2**attempt)
            continue
        suffix = " (retry)" if attempt else ""
        print(f"{label}->  {len(records):>2} records{suffix}")
        return True
    print(f"{label}->  ERROR")
    return False

def main():
    if not INPUT_PATH.exists():
        print(f"ERROR : Symbol file not found")
        return
    
    try:
        symbols = read_symbols()
    except (OSError, KeyError, ValueError, csv.Error):
        print("ERROR : Unable to process symbol file")
        return
    if not symbols:
        print("ERROR : No symbols found in symbol file")
        return
    
    total = len(symbols)
    width = len(str(total))
    
    prepare_output_dir()
    print(f"\nDownloading data for {total} symbols - {START_DATE} to {END_DATE}\n")
    
    session = create_session()
    if session is None:
        print("ERROR : Unable to create NSE session")
        return
    
    success = 0
    for index, symbol in enumerate(symbols, start=1):
        if index > 1 and (index - 1) % SESSION_REFRESH_INTERVAL == 0:
            session = create_session()
            if session is None:
                print("\nERROR : Unable to refresh NSE session")
                break
            print("\n--- SESSION REFRESHED ---\n")
        label = f"[{index:0{width}}/{total}]  {symbol:<12}"
        success += process_symbol(session, symbol, label)
    
    print(f"\nDownloaded data for {success}/{total} symbols")
    print(f"Saved to : {OUTPUT_PATH_DISPLAY}")

if __name__ == "__main__":
    main()
