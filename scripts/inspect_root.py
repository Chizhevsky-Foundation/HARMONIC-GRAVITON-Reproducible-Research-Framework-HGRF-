# scripts/inspect_root.py
import uproot, numpy as np
from collections import Counter
import sys, os

fn = sys.argv[1] if len(sys.argv) > 1 else "data/raw/filename.root"
print("Opening:", fn)
f = uproot.open(fn)
print("Keys (top-level):", f.keys())

# Encuentra los árboles (trees)
trees = [k for k in f.keys() if f[k].classname.endswith("TTree")]
print("TTrees found:", trees)

# Si hay un tree típico llamado "Events" inspecciona ramas de muones
tree_name = None
for k in f.keys():
    if "Events" in k:
        tree_name = k
        break
tree_name = tree_name or trees[0] if trees else None

if tree_name:
    tree = f[tree_name]
    print("Branches (first 40):", list(tree.keys())[:40])
    # Ejemplo: intenta leer pt de muones (ajusta según tu archivo)
    for cand in ["Muon_pt", "Muon_pt[0]", "Muon_pt_0"]:
        if cand in tree.keys():
            arr = tree[cand].array(library="np")
            print(cand, "-> shape:", arr.shape, "min/max:", np.nanmin(arr), np.nanmax(arr))
            break
else:
    print("No TTree found to inspect.")
