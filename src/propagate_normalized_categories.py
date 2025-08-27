#!/usr/bin/env python3
import os
import pandas as pd

# === CONFIG ===
structured_dir = "data/structured_csvs"   # Folder with raw structured CSVs
mappings_file = "data/mappings_cleaned.csv"  # Existing mappings
print("⚙️ Loading mappings...")

# Load mappings into DataFrame
mappings_df = pd.read_csv(mappings_file)

# Build lookup dict for Ministry → Category
mapping_dict = dict(
    zip(
        mappings_df["Ministry"].str.strip(),
        mappings_df["Category"].str.strip()
    )
)

updated_files = []
unmapped_counts = {}

print("🔄 Propagating normalized categories into structured CSVs...")

for fname in sorted(os.listdir(structured_dir)):
    if not fname.endswith(".csv"):
        continue

    path = os.path.join(structured_dir, fname)
    df = pd.read_csv(path)

    # Skip if there's no Ministry column
    if "Ministry" not in df.columns:
        continue

    # Ensure normalized_category exists
    if "normalized_category" not in df.columns:
        df["normalized_category"] = None

    # Fill normalized_category
    df["normalized_category"] = df["Ministry"].str.strip().map(mapping_dict)

    # Count missing mappings for reporting
    missing = df["normalized_category"].isna().sum()
    if missing > 0:
        unmapped_counts[fname] = missing

    # Save updated CSV in place
    df.to_csv(path, index=False)
    updated_files.append(fname)

# === SUMMARY ===
print("\n=== SUMMARY ===")
print(f"✅ Updated {len(updated_files)} structured CSVs.")
if unmapped_counts:
    print("⚠️ Some files still have missing categories:")
    for fname, count in unmapped_counts.items():
        print(f"   • {fname}: {count} missing")
else:
    print("🎉 All normalized categories successfully propagated!")

