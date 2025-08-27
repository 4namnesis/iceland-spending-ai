#!/usr/bin/env python3
import sys, os, pdfplumber, pandas as pd
from pathlib import Path

def extract_one(pdf_path, output_dir):
    output_dir = Path(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)
    basename = Path(pdf_path).stem
    out_csv = output_dir / f"{basename}_plumber.csv"
    rows = []
    try:
        with pdfplumber.open(pdf_path) as pdf:
            for page in pdf.pages:
                for table in page.extract_tables():
                    rows.extend(table)
        if rows:
            df = pd.DataFrame(rows)
            df.to_csv(out_csv, index=False)
            print(f"[OK] {out_csv}: {len(df)} rows")
        else:
            print(f"[WARN] No tables found in {pdf_path}")
    except Exception as e:
        print(f"[FAIL] {pdf_path}: {e}")

if __name__ == "__main__":
    if len(sys.argv) != 3:
        print("Usage: python3 src/extract_experiment.py [PDF_PATH] [OUTPUT_DIR]")
        sys.exit(1)
    extract_one(sys.argv[1], sys.argv[2])

