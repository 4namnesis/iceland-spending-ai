🇮🇸 iceland-spending-ai

AI pipeline for extraction, normalization, analysis, and visualization of Icelandic government spending data (Ríkisreikningur 2000–2024).
Built for real, auditable data science—not demos or toy results.

🔗 What is this?

This project:

Extracts tables and line-items from raw official Icelandic state accounts PDFs

Normalizes and reconciles changes in ministries/categories over time

Aggregates/cleans the data into a unified format for modeling

Enables visualization and statistical exploration

Deploys a model+demo for instant categorization/search of new data

All scripts are agent/LLM-friendly, modular, and reproducible.

🏗️ Directory Structure
iceland-spending-ai/
├── data/
│   ├── raw_pdfs/         # Place ALL source PDFs here (these are versioned!)
│   ├── extracted_csvs/   # 1:1 page/table extractions (auto-generated)
│   ├── normalized/       # Outputs after mapping/cleaning
│   └── processed/        # Aggregated, deduplicated files
├── src/                  # All main scripts (see below)
├── notebooks/            # For explorations, analysis, and automation
├── model/                # (optional) Model artifacts
├── app/                  # (optional) Gradio/Streamlit demo
└── requirements.txt

⚡ Quickstart

1. Clone and create environment

git clone https://github.com/4namnesis/iceland-spending-ai.git
cd iceland-spending-ai
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt


2. Place PDFs in data/raw_pdfs/

3. Run extraction (from project root)

python src/data_extraction.py --input data/raw_pdfs --output data/extracted_csvs --batch-size 3


4. Normalize categories

python src/normalize_categories.py --input data/extracted_csvs --map mappings.csv --output data/normalized


5. Aggregate all normalized CSVs

python src/aggregate_normalized.py


6. Visualize/Analyze
See the notebooks/ for example visualizations and data profiling.

🤖 Agent/LLM Usage

All processing is script-driven and version-controlled.

Do not "fix" data by hand—use mapping files/scripts for corrections.

All PDFs must be version-controlled. Do not ignore them.

🛠️ Troubleshooting

Extraction produces only empty/NaN tables?
The PDF is likely an image (scanned). Try running with OCR support:

python src/ocr_extraction.py --input data/raw_pdfs --output data/extracted_csvs


Categories are wrong?
Update mappings.csv and rerun normalization.

Push fails?
Pull & merge remote changes before pushing.

See garbage tables?
Use src/preview_extracted_csvs.py for quick sanity checks.

🧠 What’s special here?

No data fabrication.

Tracks missing/unknown ministries/categories explicitly.

Ready for Hugging Face/Gradio demo deployment.

📝 TODO / Future

Improve OCR fallback, especially for older PDFs.

Train transformer classifier for noisy/unmapped line-items.

Add Icelandic/English translation layer for broader analysis.

License

MIT
