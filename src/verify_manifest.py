#!/usr/bin/env python3
"""
src/verify_manifest.py

Verifies data/raw/*.sha256 and entries in data/raw/manifest.json.
Outputs a JSON report results/verify_manifest_report.json and prints a summary.

Usage:
  python src/verify_manifest.py                # scan data/raw for .sha256 files and manifest.json (if present)
  python src/verify_manifest.py --manifest data/raw/manifest.json
  python src/verify_manifest.py --verbose

Notes:
 - This script does NOT download remote files. It verifies local files and compares to manifest entries when provided.
 - Placeholders and URLs in manifest.json are not touched; manifest format: {"files":[{"filename":"...","sha256":"...","size_bytes":...}, ...]}
"""
import argparse
import hashlib
import json
import os
from pathlib import Path
from typing import Dict, Any

DATA_DIR = Path("data/raw")
OUT_DIR = Path("results")
OUT_DIR.mkdir(parents=True, exist_ok=True)
REPORT_PATH = OUT_DIR / "verify_manifest_report.json"

def sha256_of_file(path: Path, block_size: int = 65536) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for block in iter(lambda: f.read(block_size), b""):
            h.update(block)
    return h.hexdigest()

def read_sha256_file(path: Path) -> Dict[str,str]:
    # expects format: "<hash>  filename"
    text = path.read_text().strip()
    parts = text.split()
    if len(parts) >= 1:
        expected = parts[0]
        # attempt to find filename in same folder if present
        fname = parts[-1] if len(parts) >= 2 else ""
        return {"sha256": expected, "filename_hint": fname}
    return {"sha256":"", "filename_hint":""}

def scan_sha256_files(data_dir: Path):
    results = {}
    for sha_file in sorted(data_dir.glob("*.sha256")):
        info = read_sha256_file(sha_file)
        # infer target filename
        target = data_dir / (sha_file.stem)
        if not target.exists():
            # fallback to hint
            hint = info.get("filename_hint", "")
            if hint:
                target = data_dir / hint
        entry = {"sha_file": str(sha_file), "expected_sha256": info.get("sha256"), "target_file": str(target)}
        if target.exists():
            entry["exists"] = True
            entry["computed_sha256"] = sha256_of_file(target)
            entry["match"] = (entry["computed_sha256"].lower() == entry["expected_sha256"].lower())
            try:
                entry["size_bytes"] = target.stat().st_size
            except Exception:
                entry["size_bytes"] = None
        else:
            entry["exists"] = False
            entry["computed_sha256"] = None
            entry["match"] = False
            entry["size_bytes"] = None
        results[str(target.name)] = entry
    return results

def scan_manifest(manifest_path: Path):
    results = {}
    if not manifest_path.exists():
        return results
    txt = manifest_path.read_text()
    data = json.loads(txt)
    for f in data.get("files", []):
        fname = f.get("filename")
        expected = f.get("sha256")
        entry = {"manifest_present": True, "expected_sha256": expected, "source_url": f.get("source_url"), "manifest_entry": f}
        target = DATA_DIR / fname
        if target.exists():
            entry["exists"] = True
            entry["computed_sha256"] = sha256_of_file(target)
            entry["match"] = (entry["computed_sha256"].lower() == expected.lower()) if expected else None
            entry["size_bytes"] = target.stat().st_size
        else:
            entry["exists"] = False
            entry["computed_sha256"] = None
            entry["match"] = False
            entry["size_bytes"] = None
        results[fname] = entry
    return results

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--manifest", "-m", default=str(DATA_DIR / "manifest.json"), help="Path to manifest.json (optional)")
    ap.add_argument("--verbose", "-v", action="store_true")
    args = ap.parse_args()

    manifest_path = Path(args.manifest)
    sha_results = scan_sha256_files(DATA_DIR)
    manifest_results = scan_manifest(manifest_path) if manifest_path.exists() else {}

    summary = {
        "sha256_files_checked": len(sha_results),
        "manifest_entries_checked": len(manifest_results),
        "sha_mismatch_count": sum(1 for v in sha_results.values() if v.get("match") is False),
        "manifest_mismatch_count": sum(1 for v in manifest_results.values() if v.get("match") is False),
    }

    report = {"summary": summary, "sha256_checks": sha_results, "manifest_checks": manifest_results}
    REPORT_PATH.write_text(json.dumps(report, indent=2))
    print("Verification report written to:", REPORT_PATH)
    print("Summary:", json.dumps(summary))

    if args.verbose:
        import pprint
        pprint.pprint(report)

    # exit with non-zero if mismatches
    if summary["sha_mismatch_count"] > 0 or summary["manifest_mismatch_count"] > 0:
        print("WARNING: mismatches found.")
        raise SystemExit(2)
    else:
        print("All checked items OK.")
        raise SystemExit(0)

if __name__ == "__main__":
    main()
