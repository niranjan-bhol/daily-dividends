from pathlib import Path

import pandas as pd

BASE_DIR = Path(__file__).resolve().parent.parent
INPUT_FILE = BASE_DIR / "data" / "symbol" / "NIFTY-500.csv"
OUTPUT_FILE = BASE_DIR / "data" / "symbol" / "NIFTY-500-FILTERED-BY-COLUMN.csv"

# skiprows=[1] drops the second row of the file (the row right after the header)
# thousands="," converts strings like "1,287.90" to numbers (float, to keep decimals)
df = pd.read_csv(INPUT_FILE, skiprows=[1], usecols=["SYMBOL", "LTP"], thousands=",")
df = df.rename(columns={"SYMBOL": "symbol", "LTP": "ltp"})
df["ltp"] = pd.to_numeric(df["ltp"], errors="coerce")
df = df.dropna(subset=["ltp"])
df.to_csv(OUTPUT_FILE, index=False)

print(f"Exported {len(df)} symbols to {OUTPUT_FILE.relative_to(BASE_DIR.parent)}")
