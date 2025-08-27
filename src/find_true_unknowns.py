import os
import pandas as pd
import re
from pathlib import Path

# --- CONFIG ---
normalized_dir = Path("data/normalized")
mapping_file = Path("data/mappings_cleaned.csv")
out_report = Path("data/unknown_ministries_report.txt")

# --- Load known ministries ---
if not mapping_file.exists():
    raise FileNotFoundError(f"Missing: {mapping_file}")
mappings_df = pd.read_csv(mapping_file)
known_ministries = set(m.strip() for m in mappings_df["Ministry"].dropna().unique())

def is_probable_ministry(val):
    if pd.isna(val): return False
    s = str(val).strip()
    if not s: return False
    if len(s) > 60 or len(s) < 5: return False
    if sum(c.isdigit() for c in s) > len(s) * 0.35: return False
    if s.replace(".", "").replace(",", "").isdigit(): return False
    if not re.search(r"(ráðuneyti|stofnun|skóli|ráð|stofn|fyrirtæki|deild|svið|embætti|miðstöð|samtök)", s, re.I):
        return False
    return True

unknowns = {}
for fname in sorted(os.listdir(normalized_dir)):
    if not fname.endswith(".csv"): continue
    df = pd.read_csv(normalized_dir / fname)
    if "Ministry" not in df.columns: continue
    unknown = (
        df.loc[
            (~df["Ministry"].isin(known_ministries))
            & df["Ministry"].apply(is_probable_ministry)
        ]["Ministry"]
        .dropna().unique()
    )
    for m in unknown:
        unknowns.setdefault(m, []).append(fname)

# --- Save report ---
with open(out_report, "w", encoding="utf8") as f:
    if unknowns:
        f.write("True unknown ministries (not in mappings):\n\n")
        for ministry, files in sorted(unknowns.items()):
            f.write(f"- {ministry}    [found in: {', '.join(files)}]\n")
        print(f"🔍 Report written: {out_report} ({len(unknowns)} unknown ministries)")
    else:
        f.write("All ministries in normalized data are mapped.\n")
        print("✅ No unmapped, real ministries remain in normalized data.")

