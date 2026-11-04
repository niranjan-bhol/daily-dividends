import csv
import json
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent
INPUT_DIR = BASE_DIR / "data" / "nse" / "processed_dividends"
OUTPUT_DIR = BASE_DIR / "data" / "results"
OUTPUT_FILE = OUTPUT_DIR / "summary.csv"
OUTPUT_PATH_DISPLAY = f"{BASE_DIR.name}/{OUTPUT_FILE.relative_to(BASE_DIR)}"

COLUMNS = [
    "company",
    "symbol",
    "isin",
    "series",
    "total_dividend_amount",
    "total_dividend_percent",
    "dividend_count",
]

def calculate_result(path):
    with open(path, encoding="utf-8") as f:
        records = json.load(f)["data"]
    if not records:
        return None
    first = records[0]
    return {
        "company": first["company"],
        "symbol": first["symbol"],
        "isin": first["isin"],
        "series": first["series"],
        "total_dividend_amount": round(sum(r["dividend_amount"] for r in records), 2),
        "total_dividend_percent": round(sum(r["dividend_percent"] for r in records), 4),
        "dividend_count": sum(1 for r in records if r.get("dividend_type")),
    }

def main():
    if not INPUT_DIR.exists():
        print("ERROR : Input directory not found")
        return
    
    files = sorted(INPUT_DIR.glob("*.json"))
    if not files:
        print("ERROR : No JSON files found in input directory")
        return
    
    total = len(files)
    
    results = []
    failed = 0
    for path in files:
        try:
            result = calculate_result(path)
        except (OSError, KeyError, ValueError):
            failed += 1
            print(f"ERROR : Unable to process {path.name}")
            continue
        if result:
            results.append(result)
    
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    with open(OUTPUT_FILE, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=COLUMNS)
        writer.writeheader()
        writer.writerows(results)
    
    print(f"Processed {total - failed}/{total} files")
    print(f"Exported {len(results)} symbols to {OUTPUT_PATH_DISPLAY}")

if __name__ == "__main__":
    main()
