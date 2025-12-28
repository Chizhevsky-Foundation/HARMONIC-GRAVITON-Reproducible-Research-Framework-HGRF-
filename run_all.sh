#!/usr/bin/env bash
# run_all.sh — Orquestador simple para pipeline HGRF
# Uso: ./run_all.sh [--sample-url URL] [--entry-stop N]
set -euo pipefail

CONDA_ENV=${CONDA_ENV:-hgrf_core}
SAMPLE_URL="${1:-}"
ENTRY_STOP="${2:-}"

echo "HGRF run_all.sh starting"
echo "Conda env: ${CONDA_ENV}"
echo "Sample URL (optional): ${SAMPLE_URL}"
echo "Entry stop (optional): ${ENTRY_STOP}"

# Ensure results dir
mkdir -p results

# 1) (optional) download sample if passed as first arg
if [[ -n "${SAMPLE_URL}" ]]; then
  echo "[1/6] Downloading sample from: ${SAMPLE_URL}"
  ./scripts/download_cern_sample.sh "${SAMPLE_URL}"
fi

# Find a sample in data/raw
SAMPLE=$(ls data/raw/*.root 2>/dev/null | head -n1 || true)
if [[ -z "${SAMPLE}" ]]; then
  echo "No ROOT sample found in data/raw/. Place file or use download option."
  exit 1
fi
echo "[+] Using sample: ${SAMPLE}"

# 2) Preprocess per_particle (for analysis)
echo "[2/6] Preprocessing (per_particle)..."
conda run -n "${CONDA_ENV}" python src/data_preprocessing.py --input "${SAMPLE}" --mode per_particle --output results/preprocessed_particles.parquet --force

# 3) Analysis: compute angles
echo "[3/6] Computing angles per event..."
conda run -n "${CONDA_ENV}" python src/analysis.py --input results/preprocessed_particles.parquet --input-format parquet --output results/angles_summary.csv

# 4) Statistical tests
echo "[4/6] Running statistical tests..."
conda run -n "${CONDA_ENV}" python src/stats.py --input results/angles_summary.csv --column mean_angle_deg --output results/stats_results.json --n-toys 2000 --bootstrap-n 2000

# 5) Render notebooks to HTML
echo "[5/6] Rendering notebooks to HTML..."
conda run -n "${CONDA_ENV}" jupyter nbconvert --to html --execute notebooks/01_data_inspection.ipynb --output notebooks/01_data_inspection.html --ExecutePreprocessor.timeout=600 || true
conda run -n "${CONDA_ENV}" jupyter nbconvert --to html --execute notebooks/02_selection_and_angles.ipynb --output notebooks/02_selection_and_angles.html --ExecutePreprocessor.timeout=600 || true
conda run -n "${CONDA_ENV}" jupyter nbconvert --to html --execute notebooks/03_statistical_tests.ipynb --output notebooks/03_statistical_tests.html --ExecutePreprocessor.timeout=600 || true

# 6) Summary
echo "[6/6] Pipeline complete. Outputs in results/:"
ls -lh results | sed -n '1,200p'
echo "Done."
