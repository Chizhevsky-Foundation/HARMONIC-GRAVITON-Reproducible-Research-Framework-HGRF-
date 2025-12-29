#!/usr/bin/env python3
"""
src/analysis.py

Cálculo angular y métricas a partir de:
 - un fichero preprocesado por partícula (parquet/csv) o
 - directamente desde un ROOT (usando las ramas Muon_pt, Muon_eta, Muon_phi).

Salida:
 - results/angles_summary.csv  (por evento: n_mu, n_pairs, min/mean/max angle en grados)
 - opcional: results/angles_pairs.parquet (una fila por par, si --pairs-output se activa)

Autoría:
 - Implementación: ChatGPT
 - Método / validación: Benjamin Cabeza Durán

Uso (ejemplo):
  python src/analysis.py --input results/preprocessed_particles.parquet --input-format parquet --output results/angles_summary.csv

Notas:
 - El script usa awkward para operaciones vectorizadas; es eficiente y evita bucles Python cuando sea posible.
 - Para archivos ROOT grandes, use --entry-stop para limitar la lectura.
"""
import argparse
import json
import os
from pathlib import Path

import numpy as np
import pandas as pd

try:
    import awkward as ak
except Exception as e:
    raise SystemExit("Requires 'awkward' (pip install awkward).") from e

# optional import for ROOT reading
try:
    import uproot
except Exception:
    uproot = None


def read_preprocessed_particle_table(path):
    """Read a per-particle table (parquet or csv) and return awkward arrays grouped by event."""
    p = Path(path)
    if not p.exists():
        raise FileNotFoundError(path)
    if p.suffix.lower() in [".parquet", ".pq"]:
        df = pd.read_parquet(p)
    else:
        df = pd.read_csv(p)
    # Expect columns: run, luminosityBlock, event, mu_pt, mu_eta, mu_phi
    required = {"run", "event", "mu_pt", "mu_eta", "mu_phi"}
    if not required.issubset(set(df.columns)):
        raise RuntimeError(f"Input table missing required columns. Found columns: {list(df.columns)}")
    # group by event identifier to create jagged arrays
    # keep run/lumi/event as identifiers per event
    gb = df.groupby(["run", "luminosityBlock", "event"], sort=False)
    runs = []
    lumis = []
    events = []
    pts = []
    etas = []
    phis = []
    for (r, l, e), sub in gb:
        runs.append(int(r))
        lumis.append(int(l))
        events.append(int(e))
        pts.append(sub["mu_pt"].to_numpy())
        etas.append(sub["mu_eta"].to_numpy())
        phis.append(sub["mu_phi"].to_numpy())
    return {
        "run": np.asarray(runs),
        "luminosityBlock": np.asarray(lumis),
        "event": np.asarray(events),
        "pt": ak.Array(pts),
        "eta": ak.Array(etas),
        "phi": ak.Array(phis),
    }


def read_root_particles(root_path, entry_stop=None):
    """Read muon branches from a ROOT file and return the same structure as read_preprocessed_particle_table."""
    if uproot is None:
        raise RuntimeError("uproot is required to read ROOT files. Install with: pip install uproot")
    f = uproot.open(root_path)
    # detect tree
    keys = list(f.keys())
    tree_name = "Events" if "Events" in keys else keys[0]
    tree = f[tree_name]
    branches = list(tree.keys())
    # detect common branch names
    pt_b = "Muon_pt" if "Muon_pt" in branches else next((b for b in branches if "Muon" in b and "pt" in b.lower()), None)
    eta_b = "Muon_eta" if "Muon_eta" in branches else next((b for b in branches if "Muon" in b and "eta" in b.lower()), None)
    phi_b = "Muon_phi" if "Muon_phi" in branches else next((b for b in branches if "Muon" in b and "phi" in b.lower()), None)
    if not (pt_b and eta_b and phi_b):
        raise RuntimeError("Could not detect Muon_pt / Muon_eta / Muon_phi branches in ROOT file.")
    # identifiers
    run_b = "run" if "run" in branches else None
    lumi_b = "luminosityBlock" if "luminosityBlock" in branches else None
    evt_b = "event" if "event" in branches else None
    # read
    read_kwargs = {}
    if entry_stop is not None:
        read_kwargs["entry_stop"] = entry_stop
    mu_pt = tree[pt_b].array(library="ak", **read_kwargs)
    mu_eta = tree[eta_b].array(library="ak", **read_kwargs)
    mu_phi = tree[phi_b].array(library="ak", **read_kwargs)
    # ids
    run = tree[run_b].array(library="ak", **read_kwargs) if run_b else ak.Array([0] * len(mu_pt))
    lumi = tree[lumi_b].array(library="ak", **read_kwargs) if lumi_b else ak.Array([0] * len(mu_pt))
    evt = tree[evt_b].array(library="ak", **read_kwargs) if evt_b else ak.Array(list(range(len(mu_pt))))
    # convert ids to numpy per event (they are scalars per event)
    return {
        "run": ak.to_numpy(run),
        "luminosityBlock": ak.to_numpy(lumi),
        "event": ak.to_numpy(evt),
        "pt": mu_pt,
        "eta": mu_eta,
        "phi": mu_phi,
    }


def compute_angles_from_pt_eta_phi(pt, eta, phi):
    """
    Given jagged arrays pt, eta, phi (awkward arrays shape=(n_events, n_particles_event)),
    compute pairwise angles in degrees per event and return jagged array of angles (deg).
    """
    # compute Cartesian components (px,py,pz)
    px = pt * np.cos(phi)
    py = pt * np.sin(phi)
    pz = pt * np.sinh(eta)
    p = ak.zip({"px": px, "py": py, "pz": pz})
    # combinations of pairs per event
    pairs = ak.combinations(p, 2, axis=1)
    p0 = pairs["0"]
    p1 = pairs["1"]
    dot = p0["px"] * p1["px"] + p0["py"] * p1["py"] + p0["pz"] * p1["pz"]
    norm0 = np.sqrt(p0["px"] ** 2 + p0["py"] ** 2 + p0["pz"] ** 2)
    norm1 = np.sqrt(p1["px"] ** 2 + p1["py"] ** 2 + p1["pz"] ** 2)
    cosang = dot / (norm0 * norm1)
    # numerical safety: clip
    cosang = ak.where(ak.is_none(cosang), 1.0, cosang)
    cosang = ak.clip(cosang, -1.0, 1.0)
    ang = np.degrees(np.arccos(cosang))
    return ang  # jagged array same shape as number of pairs per event


def summarize_angles(angles_jagged):
    """
    Given jagged array of angles per event, return numpy arrays:
    n_pairs, min_angle, mean_angle, max_angle (degrees). If no pairs, n_pairs=0 and stats=nan.
    """
    n_pairs = ak.num(angles_jagged)
    min_a = ak.where(n_pairs > 0, ak.min(angles_jagged, axis=1), ak.fill_none(ak.Array([np.nan] * len(n_pairs)), np.nan))
    mean_a = ak.where(n_pairs > 0, ak.mean(angles_jagged, axis=1), ak.fill_none(ak.Array([np.nan] * len(n_pairs)), np.nan))
    max_a = ak.where(n_pairs > 0, ak.max(angles_jagged, axis=1), ak.fill_none(ak.Array([np.nan] * len(n_pairs)), np.nan))
    return ak.to_numpy(n_pairs), ak.to_numpy(min_a), ak.to_numpy(mean_a), ak.to_numpy(max_a)


def main():
    parser = argparse.ArgumentParser(description="Compute muon-pair angles per event and summarize.")
    parser.add_argument("--input", "-i", required=True, help="Input file (parquet/csv for per-particle table, or ROOT file).")
    parser.add_argument("--input-format", "-f", choices=["auto", "parquet", "csv", "root"], default="auto",
                        help="Input format. 'auto' infers from extension.")
    parser.add_argument("--entry-stop", type=int, default=None, help="If reading ROOT, limit entries (optional).")
    parser.add_argument("--output", "-o", default="results/angles_summary.csv", help="Output CSV path for per-event summary.")
    parser.add_argument("--pairs-output", default=None, help="Optional output parquet path to save per-pair rows (can be large).")
    args = parser.parse_args()

    inp = Path(args.input)
    if not inp.exists():
        raise SystemExit(f"Input not found: {inp}")

    infmt = args.input_format
    if infmt == "auto":
        if inp.suffix.lower() in [".parquet", ".pq"]:
            infmt = "parquet"
        elif inp.suffix.lower() in [".csv", ".txt"]:
            infmt = "csv"
        elif inp.suffix.lower() in [".root", ".root.gz"]:
            infmt = "root"
        else:
            raise SystemExit("Could not infer input format. Use --input-format explicitly.")

    print("Input:", inp, "format:", infmt)
    if infmt in ("parquet", "csv"):
        data = read_preprocessed_particle_table(str(inp))
    elif infmt == "root":
        data = read_root_particles(str(inp), entry_stop=args.entry_stop)
    else:
        raise SystemExit("Unsupported format")

    runs = data["run"]
    lumis = data["luminosityBlock"]
    events = data["event"]
    pt = data["pt"]
    eta = data["eta"]
    phi = data["phi"]

    print("Computing pairwise angles (deg)...")
    angles = compute_angles_from_pt_eta_phi(pt, eta, phi)

    print("Summarizing angles per event...")
    n_pairs, min_angle, mean_angle, max_angle = summarize_angles(angles)

    # Build output DataFrame
    out_df = pd.DataFrame({
        "run": np.asarray(runs),
        "luminosityBlock": np.asarray(lumis),
        "event": np.asarray(events),
        "n_mu": ak.to_numpy(ak.num(pt)),
        "n_pairs": n_pairs,
        "min_angle_deg": min_angle,
        "mean_angle_deg": mean_angle,
        "max_angle_deg": max_angle,
    })

    outp = Path(args.output)
    outp.parent.mkdir(parents=True, exist_ok=True)
    out_df.to_csv(outp, index=False)
    print("Wrote per-event summary to:", outp)

    # optional: write per-pair table
    if args.pairs_output:
        print("Writing per-pair table (may be large) to:", args.pairs_output)
        # flatten pairs into rows: run, lumi, event, angle_deg, px0,py0,pz0, px1,py1,pz1 (optional)
        # We'll construct minimal table: run,lumi,event,angle_deg
        run_rep = ak.repeat(runs, ak.num(angles))
        lumi_rep = ak.repeat(lumis, ak.num(angles))
        evt_rep = ak.repeat(events, ak.num(angles))
        # angles is jagged array of floats
        angle_flat = ak.flatten(angles)
        pair_df = pd.DataFrame({
            "run": ak.to_numpy(run_rep),
            "luminosityBlock": ak.to_numpy(lumi_rep),
            "event": ak.to_numpy(evt_rep),
            "angle_deg": ak.to_numpy(angle_flat),
        })
        pair_out = Path(args.pairs_output)
        pair_out.parent.mkdir(parents=True, exist_ok=True)
        # write parquet for efficiency
        pair_df.to_parquet(pair_out, index=False)
        print("Wrote pairs parquet to:", pair_out)

    # save provenance
    prov = {
        "input": str(inp),
        "input_format": infmt,
        "output": str(outp),
        "pairs_output": str(args.pairs_output) if args.pairs_output else None,
    }
    prov_path = outp.with_suffix(outp.suffix + ".provenance.json")
    with open(prov_path, "w") as fh:
        json.dump(prov, fh, indent=2)
    print("Wrote provenance to:", prov_path)


if __name__ == "__main__":
    main()
