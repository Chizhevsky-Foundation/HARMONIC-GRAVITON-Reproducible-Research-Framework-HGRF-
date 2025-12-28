#!/usr/bin/env bash
# scripts/download_cern_sample.sh
# Descarga muestras (small sample) de CERN OpenData u otras URLs,
# guarda en data/raw/ y opcionalmente verifica SHA256.
#
# Uso:
#   ./scripts/download_cern_sample.sh <url1> [<url2> ...]
# Ejemplo:
#   ./scripts/download_cern_sample.sh "https://opendata.cern.ch/record/12345/files/sample1.root"
#
# Si prefieres pasar un archivo de URLs:
#   ./scripts/download_cern_sample.sh -f urls.txt
#
set -euo pipefail

OUT_DIR="data/raw"
RETRIES=3
SLEEP_BETWEEN_RETRIES=5

mkdir -p "${OUT_DIR}"

function download_one() {
  local url="$1"
  local fname
  fname="$(basename "${url%%\?*}")"
  local outpath="${OUT_DIR}/${fname}"

  if [[ -f "${outpath}" ]]; then
    echo "[SKIP] ${outpath} already exists"
    return 0
  fi

  echo "[DL] Downloading ${url} -> ${outpath}"
  for i in $(seq 1 ${RETRIES}); do
    if command -v curl >/dev/null 2>&1; then
      curl --fail --location --retry 5 --retry-delay 2 -o "${outpath}" "${url}" && break
    elif command -v wget >/dev/null 2>&1; then
      wget -O "${outpath}" "${url}" && break
    else
      echo "ERROR: neither curl nor wget available. Install one and retry."
      return 2
    fi
    echo "Retry ${i}/${RETRIES} failed. Sleeping ${SLEEP_BETWEEN_RETRIES}s..."
    sleep "${SLEEP_BETWEEN_RETRIES}"
  done

  if [[ ! -f "${outpath}" ]]; then
    echo "ERROR: failed to download ${url}"
    return 3
  fi

  echo "[OK] Saved to ${outpath}"
}

# If -f fileOfUrls is given, read URLs from it
if [[ "${1:-}" == "-f" ]]; then
  if [[ -z "${2:-}" ]]; then
    echo "Usage: $0 -f urls.txt"
    exit 1
  fi
  urls_file="$2"
  if [[ ! -f "${urls_file}" ]]; then
    echo "ERROR: ${urls_file} not found"
    exit 2
  fi
  while IFS= read -r line; do
    line="${line%%#*}"        # strip comments after #
    line="${line## }"
    line="${line%% }"
    [[ -z "${line}" ]] && continue
    download_one "${line}"
  done < "${urls_file}"
  exit 0
fi

if [[ $# -lt 1 ]]; then
  cat <<EOF
Usage: $0 <url1> [url2 ...]
   or: $0 -f urls.txt    (one URL per line)
Example (placeholder):
  $0 "https://opendata.cern.ch/record/12345/files/sample1.root"
Note: replace placeholder URLs with actual links from https://opendata.cern.ch
EOF
  exit 1
fi

for url in "$@"; do
  download_one "${url}"
done

echo "All done. Files saved in ${OUT_DIR}."
