#!/usr/bin/env python3
import os
import sys
import pdfplumber
import pytesseract
from PIL import Image
import pandas as pd
from tqdm import tqdm
from pdf2image import convert_from_path
import argparse
import re

# ---------------------------
# Ministry/institution filter
# ---------------------------
def is_ministry(val):
    if pd.isna(val): return False
    s = str(val).strip()
    if not s: return False
    if len(s) > 50: return False
    if s.count(" ") > 5: return False
    # Skip numeric-only, totals, and narrative
    if s.replace(".", "").replace(",", "").isdigit():
        return False
    if any(word in s.lower() for word in [
        "rekstrarreikningur", "tekjur", "gjöld", "millj.", "kr.", "heildargjöld", "samtals", "ráðstöfun",
        "yfir", "yfirlit", "skiptust", "námu", "af", "hafa", "með", "á", "eða", "eru"
    ]):
        return False
    # Must contain some Icelandic word for institution/ministry
    if not re.search(r'(ráðuneyti|stofnun|skóli|ráð|stofn|háskóli|deild|dómstóll|samtök)', s, re.I):
        return False
    return True

# ---------------------------
# Helper: log progress to resume safely
# ---------------------------
def load_progress(log_file):
    if not os.path.exists(log_file):
        return set()
    with open(log_file, "r") as f:
        return set(line.strip() for line in f.readlines())

def update_progress(log_file, filename):
    with open(log_file, "a") as f:
        f.write(filename + "\n")

# ---------------------------
# Extract text/tables from a single PDF
# ---------------------------
def extract_pdf(pdf_path, output_csv):
    try:
        # Try fast path first: pdfplumber
        with pdfplumber.open(pdf_path) as pdf:
            rows = []
            for page in pdf.pages:
                tables = page.extract_tables()
                if tables:
                    for table in tables:
                        for row in table:
                            rows.append(row)

            # If pdfplumber found rows, try to filter and save
            if rows:
                df = pd.DataFrame(rows)
                # Only try to filter if "Ministry" column exists or can be guessed
                # Attempt to rename the most likely column to "Ministry"
                ministry_like_cols = [c for c in df.columns if "minist" in str(c).lower() or "ráðuneyti" in str(c).lower()]
                if ministry_like_cols:
                    df.rename(columns={ministry_like_cols[0]: "Ministry"}, inplace=True)
                # If there's a likely "Ministry" column, filter it
                if "Ministry" in df.columns:
                    df = df[df["Ministry"].apply(is_ministry)]
                df.to_csv(output_csv, index=False)
                return True

        # Fallback: OCR with pytesseract (slower)
        images = convert_from_path(pdf_path, dpi=300)
        ocr_text = []
        for img in images:
            text = pytesseract.image_to_string(img)
            ocr_text.append(text)

        with open(output_csv.replace(".csv", ".txt"), "w") as f:
            f.write("\n".join(ocr_text))

        return True

    except Exception as e:
        print(f"[ERROR] Failed to process {pdf_path}: {e}")
        return False

# ---------------------------
# Main pipeline
# ---------------------------
def main(args):
    input_dir = args.input
    output_dir = args.output
    batch_size = args.batch_size
    os.makedirs(output_dir, exist_ok=True)

    log_file = os.path.join(output_dir, "progress.log")
    done_files = load_progress(log_file)

    pdf_files = sorted([f for f in os.listdir(input_dir) if f.endswith(".pdf")])
    pending_files = [f for f in pdf_files if f not in done_files]

    if not pending_files:
        print("✅ All PDFs already processed.")
        sys.exit(0)

    print(f"Found {len(pending_files)} PDFs to process.")

    for i in range(0, len(pending_files), batch_size):
        batch = pending_files[i:i + batch_size]
        print(f"\n📦 Processing batch {i//batch_size + 1} ({len(batch)} files)...")

        for pdf_file in tqdm(batch, desc="Extracting"):
            pdf_path = os.path.join(input_dir, pdf_file)
            output_csv = os.path.join(output_dir, pdf_file.replace(".pdf", ".csv"))

            success = extract_pdf(pdf_path, output_csv)
            if success:
                update_progress(log_file, pdf_file)

        print(f"✅ Batch {i//batch_size + 1} complete. Memory cleared.")

    print("\n🎉 All pending PDFs processed!")

# ---------------------------
# CLI entrypoint
# ---------------------------
if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Safe PDF data extraction pipeline.")
    parser.add_argument("--input", required=True, help="Folder with raw PDFs.")
    parser.add_argument("--output", required=True, help="Folder for extracted CSVs.")
    parser.add_argument("--batch-size", type=int, default=3, help="Number of PDFs per batch.")
    args = parser.parse_args()
    main(args)

