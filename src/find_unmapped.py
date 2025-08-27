#!/usr/bin/env python3
import os
import pandas as pd

structured_dir = "data/normalized"
unmapped = set()

print(f"🔍 Scanning: {structured_dir}")

for fname in os.listdir(structured_dir):
    if not fname.endswith(".csv"):
        continue
    path = os.path.join(structured_dir, fname)
    try:
        df = pd.read_csv(path)
    except Exception as e:
        print(f"⚠️ Skipping {fname}: {e}")
        continue

    # Find ministry column
    possible_cols = ["Ministry", "category", "ráðuneyti"]
    ministry_col = None
    for col in df.columns:
        if col.strip().lower() in [p.lower() for p in possible_cols]:
            ministry_col = col
            break

    if ministry_col is None:
        continue

    # Collect only rows where normalized_category is missing
    if "normalized_category" in df.columns:
        missing = df[df["normalized_category"].isna()]
    else:
        missing = df

    unmapped.update(missing[ministry_col].dropna().str.strip().unique())

# Save new unmapped list
out_path = "data/unmapped_categories.csv"
pd.DataFrame(sorted(unmapped), columns=["Unmapped_Ministry"]).to_csv(out_path, index=False)
print(f"✅ Saved {len(unmapped)} unmapped ministries → {out_path}")

