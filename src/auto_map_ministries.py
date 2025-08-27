# src/auto_map_ministries.py

import pandas as pd
import subprocess
import json
from pathlib import Path

# Absolute or project-root relative paths
unmapped_file = Path("data/unmapped_true_ministries.csv")
mapping_file = Path("data/mappings_cleaned.csv")

# Define the official final category set
categories = [
    "Health",
    "Social & Labour",
    "Agriculture & Fisheries",
    "Education & Culture",
    "Infrastructure",
    "Finance & Economy",
    "Central Administration",
    "Misc/Missing"
]

# Load unmapped ministries
unmapped_df = pd.read_csv(unmapped_file)
try:
    mappings_df = pd.read_csv(mapping_file)
except FileNotFoundError:
    mappings_df = pd.DataFrame(columns=["Ministry", "Category"])

def classify_with_ollama(ministry, categories):
    prompt = (
        f"Given these categories: {', '.join(categories)}, "
        f"choose the single most appropriate category for the Icelandic ministry or institution below. "
        f"Ministry/Institution: \"{ministry}\" "
        f"Answer ONLY with the category name from the provided list."
    )
    result = subprocess.run(
        ["ollama", "run", "phi3:3.8b", "--json"],
        input=prompt.encode(),
        capture_output=True
    )
    try:
        output = json.loads(result.stdout.decode())["response"].strip()
        if output not in categories:
            output = "Misc/Missing"
    except Exception:
        output = "Misc/Missing"
    return output

suggested_mappings = {}
for ministry in unmapped_df["Ministry"]:
    suggested_category = classify_with_ollama(ministry, categories)
    suggested_mappings[ministry] = suggested_category
    print(f"{ministry} => {suggested_category}")

# Save new mappings
new_map = pd.DataFrame(list(suggested_mappings.items()), columns=["Ministry", "Category"])
# Remove any already-mapped
if not mappings_df.empty:
    already_mapped = set(mappings_df["Ministry"].str.strip())
    new_map = new_map[~new_map["Ministry"].str.strip().isin(already_mapped)]
full_mappings = pd.concat([mappings_df, new_map], ignore_index=True)
full_mappings.drop_duplicates(subset=["Ministry"], inplace=True)
full_mappings.to_csv(mapping_file, index=False)
print(f"\n💾 All new suggestions appended to: {mapping_file}")

