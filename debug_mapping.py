import pandas as pd
import difflib
from pathlib import Path

# CONFIG: Point to one or more normalized CSVs and your mappings
csv_path = Path("data/normalized/Rikisreikn2009Heildaryfirlit_parsed_normalized.csv")
mapping_file = Path("data/mappings_cleaned.csv")

# Load data and mapping
df = pd.read_csv(csv_path)
mappings_df = pd.read_csv(mapping_file)
mapping_keys = mappings_df["Ministry"].astype(str).str.strip().unique()
mapping_dict = dict(zip(mapping_keys, mappings_df["Category"].astype(str).str.strip()))

# What do the ministry fields *actually* look like?
print("\nSample of 'Ministry' values in your CSV:")
print(df["Ministry"].astype(str).dropna().unique()[:25])

print("\nSample of keys in your mapping dict:")
print(list(mapping_dict.keys())[:25])

# Find ministries in the data NOT in your mapping
unmapped = df["Ministry"].astype(str).dropna().unique()
unmapped = [m for m in unmapped if m.strip() and m.strip() not in mapping_dict]

print(f"\nTotal unique ministry values in CSV: {len(df['Ministry'].unique())}")
print(f"Total mapping keys: {len(mapping_dict)}")
print(f"Ministries not mapped (showing up to 25): {len(unmapped)}")
print(unmapped[:25])

# For each unmapped ministry, print closest mapping keys
print("\nSample fuzzy matches for the first 10 unmapped ministries:")
for m in unmapped[:10]:
    print(f"- {m}  =>  {difflib.get_close_matches(m.strip(), mapping_dict.keys(), n=3)}")

