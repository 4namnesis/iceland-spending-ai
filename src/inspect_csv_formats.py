#!/usr/bin/env python3
import os
import pandas as pd
import argparse
from collections import defaultdict

def inspect_csv_formats(input_dir, output_report):
    csv_files = sorted([f for f in os.listdir(input_dir) if f.endswith(".csv")])
    layout_groups = defaultdict(list)
    skipped_files = []
    
    print(f"🔍 Inspecting {len(csv_files)} CSV files...\n")

    for csv_file in csv_files:
        csv_path = os.path.join(input_dir, csv_file)
        try:
            # Read only the header row, don't load full CSV
            df = pd.read_csv(csv_path, nrows=5)
            cols = tuple(df.columns.tolist())
            layout_groups[cols].append(csv_file)
        except Exception as e:
            skipped_files.append((csv_file, str(e)))

    # Prepare a summary report
    with open(output_report, "w") as f:
        f.write("=== CSV FORMAT INSPECTION REPORT ===\n\n")
        f.write(f"Total CSV files scanned: {len(csv_files)}\n")
        f.write(f"Distinct layouts detected: {len(layout_groups)}\n\n")

        for i, (cols, files) in enumerate(layout_groups.items(), start=1):
            f.write(f"--- Layout {i} ({len(files)} files) ---\n")
            f.write("Columns: " + ", ".join(cols) + "\n")
            f.write("Files:\n")
            for name in files:
                f.write(f"  - {name}\n")
            f.write("\n")

        if skipped_files:
            f.write("=== Skipped Files ===\n")
            for name, err in skipped_files:
                f.write(f"{name}: {err}\n")

    print(f"✅ Inspection complete. Report saved to: {output_report}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Inspect CSV formats.")
    parser.add_argument("--input", required=True, help="Folder containing extracted CSVs.")
    parser.add_argument("--output", required=True, help="Path for inspection report.")
    args = parser.parse_args()

    inspect_csv_formats(args.input, args.output)

