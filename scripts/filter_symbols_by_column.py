import pandas as pd
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent
INPUT_FILE = BASE_DIR / "data" / "symbol" / "NIFTY-500.csv"
OUTPUT_FILE = BASE_DIR / "data" / "symbol" / "NIFTY-500-FILTERED-BY-COLUMN.csv"

REQUIRED_COLUMNS = ["SYMBOL", "LTP"]

def filter_by_column():
    df = pd.read_csv(INPUT_FILE, skiprows=[1], thousands=",")
    
    missing = [col for col in REQUIRED_COLUMNS if col not in df.columns]
    if missing:
        label = "column" if len(missing) == 1 else "columns"
        raise ValueError(f"Input file is missing required {label} - {', '.join(missing)}")
    
    df = df[REQUIRED_COLUMNS].rename(columns={"SYMBOL": "symbol", "LTP": "ltp"})
    df["ltp"] = pd.to_numeric(df["ltp"], errors="coerce")
    df = df.dropna(subset=["ltp"])
    df.to_csv(OUTPUT_FILE, index=False)
    return len(df)

def main():
    try:
        count = filter_by_column()
    except FileNotFoundError:
        print(f"ERROR : Input file not found at {INPUT_FILE.relative_to(BASE_DIR.parent)}")
        return
    except Exception as e:
        print(f"ERROR : {e}")
        return
    
    print(f"Exported {count} symbols to {OUTPUT_FILE.relative_to(BASE_DIR)}")

if __name__ == "__main__":
    main()
