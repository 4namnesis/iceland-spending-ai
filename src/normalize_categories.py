#!/usr/bin/env python3
import os
import pandas as pd
import argparse
from tqdm import tqdm

def normalize_categories(input_dir, mapping_file, output_dir):
    os.makedirs(output_dir, exist_ok=True)

    # Load mapping CSV and pick correct columns
    mapping_df = pd.read_csv(mapping_file)
    if mapping_df.shape[1] < 3:
        raise ValueError("❌ mappings.csv must have at least three columns: LineCode, Ministry, Category.")

    raw_col = mapping_df.columns[1]       # Ministry names
    norm_col = mapping_df.columns[2]      # Unified category names

    mapping = dict(zip(mapping_df[raw_col].str.strip(), mapping_df[norm_col].str.strip()))
    print(f"✅ Using mapping columns: '{raw_col}' → '{norm_col}'")

    # Find all extracted CSVs
    csv_files = sorted([f for f in os.listdir(input_dir) if f.endswith(".csv")])

    for csv_file in tqdm(csv_files, desc="Normalizing CSVs"):
        csv_path = os.path.join(input_dir, csv_file)
        df = pd.read_csv(csv_path)

        # Try to detect the column holding ministry names
        possible_columns = ["category", "Category", "ráðuneyti", "ministry", "Ministry"]
        category_col = None
        for col in df.columns:
            if col.lower() in [c.lower() for c in possible_columns]:
                category_col = col
                break

        if category_col is None:
            print(f"[WARNING] Couldn't find a category column in {csv_file}. Skipping.")
            continue

        # Apply mapping to normalize ministries → categories
        df["normalized_category"] = df[category_col].map(mapping)
        df["normalized_category"] = df["normalized_category"].fillna("Misc/Missing")

        # Convert amounts to millions if needed
        amount_cols = [c for c in df.columns if "kr" in c.lower() or "amount" in c.lower()]
        if amount_cols:
            df.rename(columns={amount_cols[0]: "amount_thousand_isk"}, inplace=True)
            df["amount_million_isk"] = df["amount_thousand_isk"] / 1000

        # Save cleaned CSV
        output_path = os.path.join(output_dir, csv_file.replace(".csv", "_clean.csv"))
        df.to_csv(output_path, index=False)

    print(f"✅ Normalized CSVs saved to: {output_dir}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Normalize extracted Ríkisreikningur CSVs.")
    parser.add_argument("--input", required=True, help="Folder with extracted CSVs.")
    parser.add_argument("--map", required=True, help="Mappings CSV.")
    parser.add_argument("--output", required=True, help="Folder for cleaned CSVs.")
    args = parser.parse_args()

    normalize_categories(args.input, args.map, args.output)

