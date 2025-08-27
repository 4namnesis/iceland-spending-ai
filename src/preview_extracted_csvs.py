import os
import pandas as pd
from pathlib import Path

extracted_dir = Path("data/extracted_csvs")

print(f"📂 Previewing CSVs in: {extracted_dir.resolve()}")
for fname in sorted(os.listdir(extracted_dir)):
    if not fname.endswith(".csv"):
        continue
    fpath = extracted_dir / fname
    print(f"\n==== {fname} ====")
    try:
        df = pd.read_csv(fpath, nrows=10)
        print(df.head(10))
        print(f"(Columns: {list(df.columns)})")
    except Exception as e:
        print(f"⚠️  Could not read {fname}: {e}")

