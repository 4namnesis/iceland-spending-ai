import os
import re
import pandas as pd
from rapidfuzz import process, fuzz
from unidecode import unidecode
import argparse
import pdfplumber

def normalize_text(text):
    return unidecode(text.lower().strip())

def load_ministries(mapping_file):
    df = pd.read_csv(mapping_file)
    return sorted(set(df["Ministry"].dropna().unique()), key=len, reverse=True)

def extract_ministry_amounts(text, ministries):
    results = []
    lines = [normalize_text(l) for l in text.splitlines()]
    original_lines = text.splitlines()

    for i, clean_line in enumerate(lines):
        if not clean_line:
            continue

        # Fuzzy match to detect ministry names
        match_data = process.extractOne(clean_line, ministries, scorer=fuzz.ratio)
        if not match_data:
            continue
        match, score, _ = match_data

        if score >= 80:
            # Look for numbers on this line or the next two
            context_block = " ".join(original_lines[i:i+3])
            numbers = re.findall(r"(?<!\d)(\d{1,3}(?:\.\d{3})*(?:,\d+)?)(?!\d)", context_block)
            if numbers:
                try:
                    amount = float(numbers[-1].replace(".", "").replace(",", "."))
                    results.append((match, "A-hluti", amount))
                except ValueError:
                    continue
    return results

def fallback_pdf_table_extraction(pdf_path, ministries):
    """Fallback if OCR text parsing fails — try extracting tables directly."""
    results = []
    try:
        with pdfplumber.open(pdf_path) as pdf:
            for page in pdf.pages:
                tables = page.extract_tables()
                if not tables:
                    continue
                for table in tables:
                    for row in table:
                        if not row or not any(row):
                            continue
                        text_row = " ".join([str(c) for c in row if c])
                        clean_row = normalize_text(text_row)
                        match_data = process.extractOne(clean_row, ministries, scorer=fuzz.ratio)
                        if not match_data:
                            continue
                        match, score, _ = match_data
                        if score >= 80:
                            numbers = re.findall(r"(?<!\d)(\d{1,3}(?:\.\d{3})*(?:,\d+)?)(?!\d)", text_row)
                            if numbers:
                                try:
                                    amount = float(numbers[-1].replace(".", "").replace(",", "."))
                                    results.append((match, "A-hluti", amount))
                                except ValueError:
                                    continue
    except Exception as e:
        print(f"[ERROR] Fallback PDF parsing failed: {e}")
    return results

def process_ocr_files(input_dir, mapping_file, output_dir):
    ministries = [normalize_text(m) for m in load_ministries(mapping_file)]
    os.makedirs(output_dir, exist_ok=True)

    for txt_file in os.listdir(input_dir):
        if not txt_file.endswith(".txt"):
            continue

        input_path = os.path.join(input_dir, txt_file)
        with open(input_path, "r", encoding="utf-8", errors="ignore") as f:
            text = f.read()

        extracted = extract_ministry_amounts(text, ministries)

        # Fallback to direct table parsing if OCR failed
        if not extracted:
            pdf_guess = os.path.join("data/raw_pdfs", txt_file.replace(".txt", ".pdf"))
            if os.path.exists(pdf_guess):
                print(f"[INFO] Trying PDF table fallback for {txt_file}...")
                extracted = fallback_pdf_table_extraction(pdf_guess, ministries)

        if not extracted:
            print(f"[WARNING] No matches found in {txt_file}")
            continue

        df = pd.DataFrame(extracted, columns=["Ministry", "Raw Category", "Amount"])
        output_file = os.path.join(output_dir, txt_file.replace(".txt", ".csv"))
        df.to_csv(output_file, index=False)
        print(f"✅ Processed: {txt_file} → {output_file}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--input", required=True)
    parser.add_argument("--map", required=True)
    parser.add_argument("--output", required=True)
    args = parser.parse_args()

    process_ocr_files(args.input, args.map, args.output)

