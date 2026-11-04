import json
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent
INPUT_DIR = BASE_DIR / "data" / "nse" / "filtered_dividends"
OUTPUT_DIR = BASE_DIR / "data" / "nse" / "transformed_dividends"
OUTPUT_PATH_DISPLAY = f"{BASE_DIR.name}/{OUTPUT_DIR.relative_to(BASE_DIR)}"

def prepare_output_dir():
    if OUTPUT_DIR.exists():
        for file in OUTPUT_DIR.glob("*.json"):
            file.unlink()
        print(f"Output directory exists : {OUTPUT_PATH_DISPLAY}")
        print("Cleared output directory")
    else:
        OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
        print(f"Created output directory : {OUTPUT_PATH_DISPLAY}")

def transform_records(path):
    with open(path, encoding="utf-8") as f:
        records = json.load(f)["data"]
    return [
        {
            "company": ca["comp"],
            "symbol": record["CH_SYMBOL"],
            "isin": ca["isin"],
            "series": ca["series"],
            "date": ca["exDate"],
            "close": record["CH_CLOSING_PRICE"],
            "subject": ca["subject"],
        }
        for record in records
        for ca in record.get("CA") or []
    ]

def process_file(path, label):
    try:
        records = transform_records(path)
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
    print(f"\nTransforming data for {total} symbols\n")
    
    success = 0
    for index, path in enumerate(files, start=1):
        label = f"[{index:0{width}}/{total}]  {path.stem:<12}"
        success += process_file(path, label)
    
    print(f"\nTransformed data for {success}/{total} symbols")
    print(f"Saved to : {OUTPUT_PATH_DISPLAY}")

if __name__ == "__main__":
    main()
