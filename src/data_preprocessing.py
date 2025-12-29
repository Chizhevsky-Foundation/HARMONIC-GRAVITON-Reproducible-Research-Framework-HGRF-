#!/usr/bin/env python3
"""
src/data_preprocessing.py

Lectura y preprocesado de archivos ROOT (NanoAOD / ROOT TTrees) usando uproot + awkward.
Genera:
 - modo per_event: resumen por evento (n_mu, mean_pt, etc.) -> parquet/csv
 - modo per_particle: tabla por partícula (run,event,pt,eta,phi, ...) -> parquet/csv

Uso (ejemplo):
  python src/data_preprocessing.py --input data/raw/sample.root --mode per_event --output results/angles_input.parquet

Requisitos:
  - uproot, awkward, numpy, pandas
"""
import argparse
import hashlib
import json
import os
from pathlib import Path

import numpy as np
import pandas as pd

try:
    import uproot
    import awkward as ak
except Exception as e:
    raise SystemExit("Requires uproot and awkward. Install them in the active env: pip install uproot awkward") from e


def sha256_of_file(path, block_size=65536):
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for block in iter(lambda: f.read(block_size), b""):
            h.update(block)
    return h.hexdigest()


def detect_tree(root_file):
    f = uproot.open(root_file)
    # prefer 'Events' if present, else first TTree-like key
    keys = list(f.keys())
    if "Events" in keys:
        return "Events"
    # find first key whose classname contains 'TTree'
    for k in keys:
        try:
            obj = f[k]
            cname = getattr(obj, "classname", "")
            if isinstance(cname, (bytes, bytearray)):
                cname = cname.decode(errors="ignore")
            if "TTree" in str(cname) or "TTree" in str(obj):
                return k
        except Exception:
            continue
    # fallback: first key
    return keys[0] if keys else None


def read_branches(tree, branches, entry_stop=None, library="ak"):
    """Read branches from uproot tree, return awkward arrays (or numpy if library='np')."""
    if entry_stop is not None:
        arrs = {b: tree[b].array(entry_stop=entry_stop, library=library) for b in branches}
    else:
        arrs = {b: tree[b].array(library=library) for b in branches}
    return arrs


def per_event_summary(tree, entry_stop=None):
    branches = list(tree.keys())
    # Choose typical branches
    mu_pt_b = "Muon_pt" if "Muon_pt" in branches else next((b for b in branches if "Muon" in b and "pt" in b.lower()), None)
    mu_eta_b = "Muon_eta" if "Muon_eta" in branches else next((b for b in branches if "Muon" in b and "eta" in b.lower()), None)
    mu_phi_b = "Muon_phi" if "Muon_phi" in branches else next((b for b in branches if "Muon" in b and "phi" in b.lower()), None)

    # always try to get event identifiers if present
    id_run = "run" if "run" in branches else None
    id_lumi = "luminosityBlock" if "luminosityBlock" in branches else None
    id_evt = "event" if "event" in branches else None

    # Read needed branches
    needed = [b for b in (mu_pt_b, mu_eta_b, mu_phi_b, id_run, id_lumi, id_evt) if b]
    arrs = read_branches(tree, needed, entry_stop=entry_stop, library="ak")

    mu_pt = arrs.get(mu_pt_b, ak.Array([]))
    mu_eta = arrs.get(mu_eta_b, ak.Array([]))
    mu_phi = arrs.get(mu_phi_b, ak.Array([]))

    # per-event metrics
    n_mu = ak.num(mu_pt)
    mean_pt = ak.where(n_mu > 0, ak.mean(mu_pt, axis=1), ak.zeros_like(n_mu, dtype=float))
    min_pt = ak.where(n_mu > 0, ak.min(mu_pt, axis=1), ak.zeros_like(n_mu, dtype=float))
    max_pt = ak.where(n_mu > 0, ak.max(mu_pt, axis=1), ak.zeros_like(n_mu, dtype=float))

    # optional event ids
    run = arrs.get(id_run, ak.zeros_like(n_mu, dtype=int))
    lumi = arrs.get(id_lumi, ak.zeros_like(n_mu, dtype=int))
    evt = arrs.get(id_evt, ak.Array(np.arange(len(n_mu)))

    df = pd.DataFrame({
        "run": ak.to_numpy(run),
        "luminosityBlock": ak.to_numpy(lumi),
        "event": ak.to_numpy(evt),
        "n_mu": ak.to_numpy(n_mu),
        "mean_mu_pt": ak.to_numpy(mean_pt),
        "min_mu_pt": ak.to_numpy(min_pt),
        "max_mu_pt": ak.to_numpy(max_pt),
    })
    return df


def per_particle_table(tree, entry_stop=None):
    branches = list(tree.keys())
    mu_pt_b = "Muon_pt" if "Muon_pt" in branches else next((b for b in branches if "Muon" in b and "pt" in b.lower()), None)
    mu_eta_b = "Muon_eta" if "Muon_eta" in branches else next((b for b in branches if "Muon" in b and "eta" in b.lower()), None)
    mu_phi_b = "Muon_phi" if "Muon_phi" in branches else next((b for b in branches if "Muon" in b and "phi" in b.lower()), None)

    id_run = "run" if "run" in branches else None
    id_lumi = "luminosityBlock" if "luminosityBlock" in branches else None
    id_evt = "event" if "event" in branches else None

    needed = [b for b in (mu_pt_b, mu_eta_b, mu_phi_b, id_run, id_lumi, id_evt) if b]
    arrs = read_branches(tree, needed, entry_stop=entry_stop, library="ak")

    if not (mu_pt_b and mu_eta_b and mu_phi_b):
        raise RuntimeError("No se detectaron ramas muon (pt/eta/phi) para generar tabla por partícula.")

    mu_pt = arrs[mu_pt_b]
    mu_eta = arrs[mu_eta_b]
    mu_phi = arrs[mu_phi_b]

    # event ids
    run = arrs.get(id_run, ak.zeros_like(mu_pt, dtype=int))
    lumi = arrs.get(id_lumi, ak.zeros_like(mu_pt, dtype=int))
    evt = arrs.get(id_evt, ak.Array(np.arange(len(mu_pt)))

    # repeat per muon using awkward.repeat and flatten
    counts = ak.num(mu_pt)
    # repeat event ids to match per-muon counts, then flatten
    run_rep = ak.flatten(ak.repeat(run, counts))
    lumi_rep = ak.flatten(ak.repeat(lumi, counts))
    evt_rep = ak.flatten(ak.repeat(evt, counts))

    pt_flat = ak.flatten(mu_pt)
    eta_flat = ak.flatten(mu_eta)
    phi_flat = ak.flatten(mu_phi)

    table = ak.zip({
        "run": run_rep,
        "luminosityBlock": lumi_rep,
        "event": evt_rep,
        "mu_pt": pt_flat,
        "mu_eta": eta_flat,
        "mu_phi": phi_flat,
    })

    # convert to pandas DataFrame (1D)
    df = ak.to_pandas(table)  # returns DataFrame
    # ensure index reset
    df = df.reset_index(drop=True)
    return df


def main():
    parser = argparse.ArgumentParser(description="Preprocess ROOT files (NanoAOD) into reduced tables.")
    parser.add_argument("--input", "-i", required=True, help="Input ROOT file path")
    parser.add_argument("--tree", "-t", default=None, help="Tree name (default: detect automatically)")
    parser.add_argument("--mode", "-m", choices=["per_event", "per_particle"], default="per_event")
    parser.add_argument("--entry-stop", type=int, default=None, help="Maximum number of entries to read from the tree")
    parser.add_argument("--output", "-o", default="results/preprocessed.parquet", help="Output file (parquet or csv). Extension decides format.")
    parser.add_argument("--force", action="store_true", help="Overwrite output if exists")
    args = parser.parse_args()

    inp = Path(args.input)
    if not inp.exists():
        raise SystemExit(f"Input file not found: {inp}")

    outp = Path(args.output)
    outp.parent.mkdir(parents=True, exist_ok=True)
    if outp.exists() and not args.force:
        raise SystemExit(f"Output exists: {outp}. Use --force to overwrite.")

    # provenance
    prov = {
        "input_path": str(inp),
        "input_sha256": sha256_of_file(inp),
        "mode": args.mode,
        "entry_stop": args.entry_stop,
    }

    # open file and choose tree
    f = uproot.open(str(inp))
    tree_name = args.tree or detect_tree(str(inp))
    if tree_name is None:
        raise SystemExit("No tree detected in ROOT file.")
    tree = f[tree_name]

    if args.mode == "per_event":
        df = per_event_summary(tree, entry_stop=args.entry_stop)
    else:
        df = per_particle_table(tree, entry_stop=args.entry_stop)

    # save output
    if outp.suffix.lower() in [".parquet", ".pq"]:
        df.to_parquet(outp, index=False)
    else:
        df.to_csv(outp, index=False)

    # save provenance
    prov_path = outp.with_suffix(outp.suffix + ".provenance.json")
    with open(prov_path, "w") as fh:
        json.dump(prov, fh, indent=2)

    print("Wrote:", outp)
    print("Provenance written to:", prov_path)


if __name__ == "__main__":
    main()
