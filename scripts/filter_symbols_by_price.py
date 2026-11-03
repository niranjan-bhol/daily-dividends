import pandas as pd
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent
INPUT_FILE = BASE_DIR / "data" / "symbol" / "NIFTY-500-FILTERED-BY-COLUMN.csv"
OUTPUT_FILE = BASE_DIR / "data" / "symbol" / "NIFTY-500-FILTERED-BY-PRICE.csv"

MAX_PRICE = 5000

def filter_by_price():
    df = pd.read_csv(INPUT_FILE)
    
    if "ltp" not in df.columns:
        raise ValueError("Input file is missing required column - ltp")
    
    df = df[df["ltp"] <= MAX_PRICE]
    df.to_csv(OUTPUT_FILE, index=False)
    return len(df)

def main():
    try:
        count = filter_by_price()
    except FileNotFoundError:
        print(f"ERROR : Input file not found at {INPUT_FILE.relative_to(BASE_DIR.parent)}")
        return
    except Exception as e:
        print(f"ERROR : {e}")
        return
    
    print(f"Exported {count} symbols to {OUTPUT_FILE.relative_to(BASE_DIR)}")

if __name__ == "__main__":
    main()
