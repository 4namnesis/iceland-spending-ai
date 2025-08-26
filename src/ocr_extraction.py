#!/usr/bin/env python3
import os
import sys
import pytesseract
from pdf2image import convert_from_path
from tqdm import tqdm
import argparse
import json

# ---------------------------
# Progress tracking
# ---------------------------
def load_progress(log_file):
    if not os.path.exists(log_file):
        return {}
    with open(log_file, "r") as f:
        return json.load(f)

def save_progress(log_file, data):
    with open(log_file, "w") as f:
        json.dump(data, f, indent=2)

# ---------------------------
# OCR single page, safe mode
# ---------------------------
def ocr_page_safe(pdf_path, page_num, dpi):
    """OCR a single page with fallback DPI & language handling."""
    try:
        images = convert_from_path(
            pdf_path,
            dpi=dpi,
            first_page=page_num,
            last_page=page_num
        )
        img = images[0]

        # Retry lower DPI if page is huge (>20MB)
        if len(img.tobytes()) > 20 * 1024 * 1024:
            print(f"⚠️  Page {page_num} too big, retrying at 100 DPI…")
            images = convert_from_path(
                pdf_path,
                dpi=100,
                first_page=page_num,
                last_page=page_num
            )
            img = images[0]

        # Always try Icelandic OCR first
        try:
            text = pytesseract.image_to_string(img, lang="isl", config="--oem 1 --psm 4")
            if text.strip() == "":
                # fallback to English if page returns nothing
                text = pytesseract.image_to_string(img, lang="eng", config="--oem 1 --psm 4")
        finally:
            del img

        return text

    except Exception as e:
        print(f"[ERROR] OCR failed on {pdf_path} (page {page_num}): {e}")
        return None

# ---------------------------
# OCR a PDF (page by page)
# ---------------------------
def ocr_pdf(pdf_path, output_txt, start_page=1, preview=False):
    try:
        # Count total pages efficiently
        images = convert_from_path(pdf_path, dpi=30, first_page=1, last_page=1)
        total_pages = len(convert_from_path(pdf_path, dpi=30))  # safer scan
        del images

        end_page = start_page if preview else total_pages

        for i in range(start_page, end_page + 1):
            text = ocr_page_safe(pdf_path, i, dpi=150)
            if text is None:
                continue

            # Append to file incrementally
            with open(output_txt, "a", encoding="utf-8") as f:
                f.write(f"=== PAGE {i} ===\n{text.strip()}\n\n")

        return total_pages

    except Exception as e:
        print(f"[ERROR] OCR failed on {pdf_path}: {e}")
        return None

# ---------------------------
# Main driver
# ---------------------------
def main(args):
    input_dir = args.input
    output_dir = args.output
    batch_size = args.batch_size
    preview = args.preview

    os.makedirs(output_dir, exist_ok=True)
    log_file = os.path.join(output_dir, "progress.json")
    progress = load_progress(log_file)

    pdf_files = sorted([f for f in os.listdir(input_dir) if f.endswith(".pdf")])
    pending_files = [f for f in pdf_files if f not in progress or not progress[f].get("done", False)]

    if not pending_files:
        print("✅ All PDFs OCR'd.")
        sys.exit(0)

    print(f"Found {len(pending_files)} PDFs to OCR.")

    for i in range(0, len(pending_files), batch_size):
        batch = pending_files[i:i + batch_size]
        print(f"\n📦 Processing batch {i // batch_size + 1} ({len(batch)} files)…")

        for pdf_file in tqdm(batch, desc="OCRing PDFs"):
            pdf_path = os.path.join(input_dir, pdf_file)
            output_txt = os.path.join(output_dir, pdf_file.replace(".pdf", ".txt"))
            start_page = progress.get(pdf_file, {}).get("last_page", 1)

            total_pages = ocr_pdf(pdf_path, output_txt, start_page, preview=preview)
            if total_pages:
                progress[pdf_file] = {"done": preview or True, "last_page": total_pages}
                save_progress(log_file, progress)

        print(f"✅ Batch {i // batch_size + 1} complete.")

    if preview:
        print("\n🔍 Preview mode finished. Only first pages processed.")
    else:
        print("\n🎉 OCR finished! Text files saved to:", output_dir)

# ---------------------------
# Entrypoint
# ---------------------------
if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Memory-safe OCR for PDFs with resume + preview support.")
    parser.add_argument("--input", required=True, help="Folder with raw PDFs.")
    parser.add_argument("--output", required=True, help="Folder for OCR'd .txt files.")
    parser.add_argument("--batch-size", type=int, default=1, help="PDFs per batch (default: 1).")
    parser.add_argument("--preview", action="store_true", help="Process only the first page of each PDF.")
    args = parser.parse_args()
    main(args)

