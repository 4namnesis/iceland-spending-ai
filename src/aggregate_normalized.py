import os
import pandas as pd
from pathlib import Path

normalized_dir = Path("data/normalized")
outfile = Path("data/processed/all_years_normalized.csv")
outfile.parent.mkdir(parents=True, exist_ok=True)

frames = []

for fname in sorted(os.listdir(normalized_dir)):
    if not fname.endswith(".csv"):
        continue
    try:
        df = pd.read_csv(normalized_dir / fname)

        # -- Ensure columns are strings for .str ops --
        if "Ministry" in df.columns:
            df["Ministry"] = df["Ministry"].astype(str)
        if "normalized_category" in df.columns:
            df["normalized_category"] = df["normalized_category"].astype(str)

        # Only keep rows with valid (not-NA) ministries and mapped categories
        has_ministry = df["Ministry"].notna() & (df["Ministry"].str.strip() != "")
        if "normalized_category" in df.columns:
            has_category = (
                df["normalized_category"].notna()
                & (df["normalized_category"].str.strip() != "Misc/Missing")
                & (df["normalized_category"].str.lower().str.strip() != "nan")
            )
            df = df[has_ministry & has_category]
        else:
            df = df[has_ministry]

        if not df.empty:
            df["source_file"] = fname
            frames.append(df)
    except Exception as e:
        print(f"❌ Failed to process {fname}: {e}")

if frames:
    master = pd.concat(frames, ignore_index=True)
    master.to_csv(outfile, index=False)
    print(f"✅ Aggregated {len(frames)} normalized files → {outfile} ({len(master)} rows)")
else:
    print("❌ No valid data found to aggregate!")

