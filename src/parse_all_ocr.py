import os
import re
import pandas as pd

# Paths
ocr_dir = "data/ocr_text"
output_dir = "data/structured_csvs"
os.makedirs(output_dir, exist_ok=True)

# Regex for Icelandic formatted numbers (1.234.567 or 123.456,78)
amount_pattern = re.compile(r"\b\d{1,3}(?:\.\d{3})*(?:,\d+)?\b")

def parse_ocr_file(file_path):
    """Parse a single OCR'd TXT file into structured data."""
    with open(file_path, "r", encoding="utf-8", errors="ignore") as f:
        text = f.read()

    lines = [l.strip() for l in text.splitlines() if l.strip()]

    entries = []
    current_ministry = None
    current_subcategory = None

    for i, line in enumerate(lines):
        # Detect ministries
        if re.search(r"[Rr]áðuneyti", line):
            current_ministry = line
            current_subcategory = None
            continue

        # Detect subcategories — usually short, no numbers
        if current_ministry and not amount_pattern.search(line) and len(line.split()) < 6:
            current_subcategory = line
            continue

        # Detect amounts
        amounts = amount_pattern.findall(line)
        if amounts:
            amount_clean = amounts[-1].replace(".", "").replace(",", ".")
            try:
                amount_val = float(amount_clean)
            except ValueError:
                continue

            entries.append({
                "Ministry": current_ministry,
                "Subcategory": current_subcategory,
                "LineItem": line,
                "Amount_thousands_ISK": amount_val
            })

    return pd.DataFrame(entries)

# Process all OCR’d text files
all_dfs = []
for txt_file in os.listdir(ocr_dir):
    if not txt_file.endswith(".txt"):
        continue

    file_path = os.path.join(ocr_dir, txt_file)
    print(f"📄 Parsing: {txt_file}")

    df = parse_ocr_file(file_path)
    if df.empty:
        print(f"⚠️  No data extracted from {txt_file}")
        continue

    # Extract year if possible from filename
    year_match = re.search(r"(20\d{2}|19\d{2})", txt_file)
    df["Year"] = int(year_match.group(1)) if year_match else None

    # Save individual CSV
    out_path = os.path.join(output_dir, txt_file.replace(".txt", "_parsed.csv"))
    df.to_csv(out_path, index=False)
    print(f"✅ Saved: {out_path}")

    all_dfs.append(df)

# Combine everything into one master CSV
if all_dfs:
    master_df = pd.concat(all_dfs, ignore_index=True)
    master_df.to_csv(os.path.join(output_dir, "all_years_parsed.csv"), index=False)
    print(f"\n🎉 Master dataset saved → {output_dir}/all_years_parsed.csv")
else:
    print("\n⚠️  No data extracted from any files!")

