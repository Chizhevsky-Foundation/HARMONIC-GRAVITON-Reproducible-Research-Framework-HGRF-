#!/usr/bin/env python3
# scripts/inspect_root.py -- versión robusta
import uproot, numpy as np, awkward as ak, sys, os
from pprint import pprint

def safe_flat_numpy(arr):
    # Convierte un awkward array (posiblemente jagged) a numpy flat 1-D array
    try:
        flat = ak.flatten(arr)
    except Exception:
        # si arr no es awkward, intentar convertir directamente
        try:
            return np.asarray(arr).ravel()
        except Exception:
            return np.array([])
    # ak.to_numpy puede fallar si no es regular; usar np.asarray sobre la vista
    try:
        return np.asarray(flat)
    except Exception:
        # fallback a lista -> numpy
        try:
            return np.array(ak.to_list(flat))
        except Exception:
            return np.array([])

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python scripts/inspect_root.py <file.root>")
        sys.exit(1)
    fn = sys.argv[1]
    if not os.path.exists(fn):
        print("File not found:", fn)
        sys.exit(2)

    print("Opening:", fn)
    f = uproot.open(fn)
    keys = list(f.keys())
    print("Keys (top-level):", keys)

    # Detectar TTrees
    tree_names = []
    for k in keys:
        try:
            obj = f[k]
            cname = obj.classname.decode() if isinstance(obj.classname, (bytes, bytearray)) else str(getattr(obj, "classname", ""))
            if "TTree" in cname or "TTree" in str(obj):
                tree_names.append(k)
        except Exception:
            pass

    # Fallback
    if not tree_names and "Events" in keys:
        tree_names = ["Events"]

    if not tree_names:
        print("No TTrees found:", keys)
        sys.exit(0)

    tree_name = tree_names[0]
    print("Using tree:", tree_name)
    tree = f[tree_name]
    try:
        n_entries = getattr(tree, "num_entries", None)
    except Exception:
        n_entries = None
    print("Number of entries (approx):", n_entries)

    branches = list(tree.keys())
    print("Number of branches:", len(branches))
    print("First 60 branches:")
    pprint(branches[:60])

    # Heurística para encontrar ramas de pt/muon
    candidate_pt = [b for b in branches if ("Muon" in b or "mu" in b.lower()) and "pt" in b.lower()]
    print("Candidate pt branches (heuristic):", candidate_pt[:10])

    pt_branch = None
    for cand in ["Muon_pt", "Muon_pt_0", "muon_pt", "mu_pt", "Muon_pt0"]:
        if cand in branches:
            pt_branch = cand
            break
    if not pt_branch and candidate_pt:
        pt_branch = candidate_pt[0]

    if pt_branch:
        print("Reading pt branch:", pt_branch)
        try:
            arr = tree[pt_branch].array(entry_stop=10000, library="ak")
        except Exception:
            arr = tree[pt_branch].array(entry_stop=10000, library="np")
        flat_np = safe_flat_numpy(arr)
        if flat_np.size:
            print("pt sample size:", flat_np.size)
            print("min/max/mean:", float(np.nanmin(flat_np)), float(np.nanmax(flat_np)), float(np.nanmean(flat_np)))
        else:
            print("pt branch read but no numeric data found or empty after flattening.")
    else:
        print("No pt-like branch auto-detected. Revisa la lista de ramas arriba.")
