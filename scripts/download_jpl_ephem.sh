#!/usr/bin/env bash
# scripts/download_jpl_ephem.sh
# Wrapper to download ephemerides from JPL Horizons using astroquery.
# Saves CSV to data/raw/jpl_<TARGET>_<START>_<STOP>.csv
#
# Usage:
#   ./scripts/download_jpl_ephem.sh TARGET START STOP STEP
# Example:
#   ./scripts/download_jpl_ephem.sh "10" "2025-01-01" "2025-12-31" "1 d"
# Notes:
# - TARGET: Horizons target id or name (e.g., '10' for Sun center, '199' Earth-Moon barycenter, '399' Earth).
# - START/STOP: ISO dates or "YYYY-MM-DD".
# - STEP: step size accepted by Horizons (e.g., "1 d", "1 h").
# - Requires Python with package `astroquery` installed in the active environment.
set -euo pipefail

if [[ $# -lt 4 ]]; then
  cat <<EOF
Usage: $0 TARGET START STOP STEP
Example: $0 "10" "2025-01-01" "2025-12-31" "1 d"
This will save: data/raw/jpl_TARGET_START_STOP.csv
EOF
  exit 1
fi

TARGET="$1"
START="$2"
STOP="$3"
STEP="$4"

OUT_DIR="data/raw"
mkdir -p "${OUT_DIR}"

# Safe filename
safe_target=$(echo "${TARGET}" | tr -c '[:alnum:]_-' '_')
safe_start=$(echo "${START}" | tr -c '[:alnum:]_-' '_')
safe_stop=$(echo "${STOP}" | tr -c '[:alnum:]_-' '_')
OUTFILE="${OUT_DIR}/jpl_${safe_target}_${safe_start}_${safe_stop}.csv"

echo "[INFO] Will request Horizons: TARGET=${TARGET}, START=${START}, STOP=${STOP}, STEP=${STEP}"
echo "[INFO] Output -> ${OUTFILE}"

# Ensure python and astroquery available
if ! command -v python >/dev/null 2>&1; then
  echo "ERROR: python not found in PATH. Activate the appropriate env or install Python."
  exit 2
fi

python - <<PY
from datetime import datetime
import sys
try:
    from astroquery.jplhorizons import Horizons
except Exception as e:
    print("ERROR: astroquery.jplhorizons not available. Install with: pip install astroquery")
    sys.exit(3)

target="${TARGET}"
start="${START}"
stop="${STOP}"
step="${STEP}"

# Query example: obtaining vector and states (customize 'quantities' as needed)
obj = Horizons(id=target, location="@sun", epochs={'start': start, 'stop': stop, 'step': step})
# Options: 'vectors' or 'ephemerides' methods. Use 'ephemerides' for human-readable table.
try:
    eph = obj.ephemerides()
except Exception as ex:
    print("ERROR fetching ephemeris:", ex)
    sys.exit(4)

# Save to CSV
out_file = "${OUTFILE}"
eph.to_csv(out_file, index=False)
print(f"[OK] Saved ephemerides to {out_file}")
PY

echo "[DONE]"
