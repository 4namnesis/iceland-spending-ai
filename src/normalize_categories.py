#!/usr/bin/env python3
import os
import pandas as pd
import argparse
from tqdm import tqdm

def apply_normalization(input_dir, mapping_file, output_dir):
    os.makedirs(output_dir, exist_ok=True)

    # Load mapping CSV
    mapping_df = pd.read_csv(mapping_file)
    if mapping_df.shape[1] < 3:
        raise ValueError("❌ mappings_cleaned.csv must have 3 columns: LineCode, Ministry, Category")

    raw_col = mapping_df.columns[1]       # Ministry
    norm_col = mapping_df.columns[2]      # Category

    mapping = dict(zip(mapping_df[raw_col].astype(str).str.strip(),
                       mapping_df[norm_col].astype(str).str.strip()))

    global_unmapped = set()
    csv_files = sorted([f for f in os.listdir(input_dir) if f.endswith(".csv")])

    for csv_file in tqdm(csv_files, desc="Normalizing CSVs"):
        csv_path = os.path.join(input_dir, csv_file)
        df = pd.read_csv(csv_path)

        # Detect ministry/category column
        possible_columns = ["category", "Category", "ráðuneyti", "ministry", "Ministry"]
        category_col = next((col for col in df.columns if col.lower() in [c.lower() for c in possible_columns]), None)

        if category_col is None:
            print(f"[⚠️] Couldn't find a category column in {csv_file}. Skipping.")
            continue

        # Apply mapping
        df["normalized_category"] = df[category_col].map(mapping)
        df["normalized_category"] = df["normalized_category"].fillna("Misc/Missing")

        # Find unmapped ministries
        unmapped = set(df.loc[df["normalized_category"] == "Misc/Missing", category_col].unique())
        # Clean: drop NaNs, convert everything to str
        unmapped = {str(x).strip() for x in unmapped if pd.notna(x) and str(x).strip() != ""}
        if unmapped:
            print(f"⚠️ {csv_file} → {len(unmapped)} unmapped categories.")
            global_unmapped |= unmapped

        # Convert amounts to millions if possible
        amount_cols = [c for c in df.columns if "kr" in c.lower() or "amount" in c.lower()]
        if amount_cols:
            df.rename(columns={amount_cols[0]: "amount_thousand_isk"}, inplace=True)
            df["amount_million_isk"] = df["amount_thousand_isk"] / 1000

        # Save cleaned CSV
        output_path = os.path.join(output_dir, csv_file.replace(".csv", "_clean.csv"))
        df.to_csv(output_path, index=False)

    # Final summary
    print("\n=== SUMMARY ===")
    print(f"✅ Processed {len(csv_files)} files")
    print(f"⚠️ {len(global_unmapped)} total unmapped categories")

    # Write a separate file for unmapped categories
    unmapped_path = os.path.join(os.path.dirname(mapping_file), "unmapped_categories.csv")
    pd.DataFrame(sorted(global_unmapped), columns=["Unmapped_Ministry"]).to_csv(unmapped_path, index=False)
    print(f"📝 Unmapped ministries saved to: {unmapped_path}")

    # Auto-append missing mappings to mappings_cleaned.csv
    existing_ministries = set(mapping_df[raw_col].astype(str).str.strip())
    new_entries = sorted([m for m in global_unmapped if m not in existing_ministries])

    if new_entries:
        print(f"➕ Adding {len(new_entries)} new rows to mappings_cleaned.csv ...")
        new_rows = pd.DataFrame({
            "LineCode": [""] * len(new_entries),
            raw_col: new_entries,
            norm_col: [""] * len(new_entries)
        })
        updated_df = pd.concat([mapping_df, new_rows], ignore_index=True)
        updated_df.to_csv(mapping_file, index=False)
        print(f"✅ Updated mappings_cleaned.csv with {len(new_entries)} new entries")
    else:
        print("✅ No new unmapped categories found.")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Normalize extracted Ríkisreikningur CSVs.")
    parser.add_argument("--apply", action="store_true", help="Apply mappings to normalize CSVs.")
    parser.add_argument("--input", required=True, help="Folder with extracted CSVs.")
    parser.add_argument("--map", required=True, help="Mappings CSV.")
    parser.add_argument("--output", required=True, help="Folder for cleaned CSVs.")
    args = parser.parse_args()

    if args.apply:
        apply_normalization(args.input, args.map, args.output)
