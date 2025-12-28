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

def try_ephemerides(tgt, loc, start, stop, step):
    try:
        obj = Horizons(id=tgt, location=loc, epochs={'start': start, 'stop': stop, 'step': step})
        eph = obj.ephemerides()
        return eph, loc
    except Exception as ex:
        return None, ex

print(f"[INFO] Trying primary request: target={target}, location=@sun")
eph, info = try_ephemerides(target, "@sun", start, stop, step)
if eph is None:
    print("[WARN] Primary request failed:", info)
    # Try fallback locations (order chosen for robustness)
    fallbacks = ["@0", "399", "@399", "500@0"]
    for fb in fallbacks:
        print(f"[INFO] Trying fallback location: {fb}")
        eph, info = try_ephemerides(target, fb, start, stop, step)
        if eph is not None:
            print(f"[OK] Success with fallback location: {fb}")
            break

if eph is None:
    print("ERROR fetching ephemeris: All attempts failed. Last error:", info)
    sys.exit(4)

out_file = "${OUTFILE}"
eph.to_csv(out_file, index=False)
print(f"[OK] Saved ephemerides to {out_file}")
PY
