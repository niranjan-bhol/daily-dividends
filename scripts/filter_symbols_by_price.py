from pathlib import Path

import pandas as pd

BASE_DIR = Path(__file__).resolve().parent.parent
INPUT_FILE = BASE_DIR / "data" / "symbol" / "NIFTY-500-FILTERED-BY-COLUMN.csv"
OUTPUT_FILE = BASE_DIR / "data" / "symbol" / "NIFTY-500-FILTERED-BY-PRICE.csv"

df = pd.read_csv(INPUT_FILE)
df = df[df["ltp"] <= 5000]
df.to_csv(OUTPUT_FILE, index=False)

print(f"Exported {len(df)} symbols to {OUTPUT_FILE.relative_to(BASE_DIR.parent)}")
