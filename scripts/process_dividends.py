import re
import json
from datetime import datetime
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent
INPUT_DIR = BASE_DIR / "data" / "nse" / "transformed_dividends"
OUTPUT_DIR = BASE_DIR / "data" / "nse" / "processed_dividends"
OUTPUT_PATH_DISPLAY = f"{BASE_DIR.name}/{OUTPUT_DIR.relative_to(BASE_DIR)}"

AMOUNT_PATTERN = re.compile(r"\bR[se]\.?\s*(\d+(?:\.\d+)?)", re.IGNORECASE)

def prepare_output_dir():
    if OUTPUT_DIR.exists():
        for file in OUTPUT_DIR.glob("*.json"):
            file.unlink()
        print(f"Output directory exists : {OUTPUT_PATH_DISPLAY}")
        print("Cleared output directory")
    else:
        OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
        print(f"Created output directory : {OUTPUT_PATH_DISPLAY}")

def get_dividend_type(subject):
    subject = subject.lower()
    if "interim" in subject:
        return "interim"
    if "special" in subject:
        return "special"
    return "final"

def get_dividend_amount(subject):
    match = AMOUNT_PATTERN.search(subject)
    return float(match.group(1)) if match else 0.0

def process_records(path):
    with open(path, encoding="utf-8") as f:
        records = json.load(f)["data"]
    processed = []
    for record in records:
        close = record["close"]
        amount = get_dividend_amount(record["subject"])
        processed.append({
            "company": record["company"],
            "symbol": record["symbol"],
            "isin": record["isin"],
            "series": record["series"],
            "date": datetime.strptime(record["date"], "%d-%b-%Y").date().isoformat(),
            "close": close,
            "dividend_type": get_dividend_type(record["subject"]),
            "dividend_amount": amount,
            "dividend_percent": round(amount / close * 100, 4) if close else 0.0,
        })
    return processed

def process_file(path, label):
    try:
        records = process_records(path)
        with open(OUTPUT_DIR / path.name, "w", encoding="utf-8") as f:
            json.dump({"data": records}, f, indent=2, ensure_ascii=False)
    except (OSError, KeyError, ValueError):
        print(f"{label}->  ERROR")
        return False
    print(f"{label}->  {len(records):>1} records")
    return True

def main():
    if not INPUT_DIR.exists():
        print("ERROR : Input directory not found")
        return
    
    files = sorted(INPUT_DIR.glob("*.json"))
    if not files:
        print("ERROR : No JSON files found in input directory")
        return
    
    total = len(files)
    width = len(str(total))
    
    prepare_output_dir()
    print(f"\nProcessing data for {total} symbols\n")
    
    success = 0
    for index, path in enumerate(files, start=1):
        label = f"[{index:0{width}}/{total}]  {path.stem:<12}"
        success += process_file(path, label)
    
    print(f"\nProcessed data for {success}/{total} symbols")
    print(f"Saved to : {OUTPUT_PATH_DISPLAY}")

if __name__ == "__main__":
    main()
