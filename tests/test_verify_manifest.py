import hashlib
import json
from pathlib import Path

import src.verify_manifest as vm


def test_scan_sha256_and_manifest(tmp_path):
    # Setup: crear data/raw con un archivo y su .sha256 y manifest.json
    data_dir = tmp_path / "data" / "raw"
    data_dir.mkdir(parents=True)
    sample = data_dir / "sample.root"
    sample.write_bytes(b"dummy content for hashing")  # archivo de prueba

    # calcular sha y escribir .sha256
    sha = hashlib.sha256(sample.read_bytes()).hexdigest()
    sha_file = data_dir / "sample.root.sha256"
    sha_file.write_text(f"{sha}  sample.root")

    # crear manifest.json con la misma entrada
    manifest = data_dir / "manifest.json"
    manifest_content = {"files": [{"filename": "sample.root", "sha256": sha, "size_bytes": sample.stat().st_size, "source_url": ""}]}
    manifest.write_text(json.dumps(manifest_content))

    # Ejecutar funciones del módulo
    sha_results = vm.scan_sha256_files(data_dir)
    manifest_results = vm.scan_manifest(manifest)

    # Assertions: el archivo existe y coincide
    assert "sample.root" in sha_results
    s = sha_results["sample.root"]
    assert s["exists"] is True
    assert s["match"] is True
    assert "sample.root" in manifest_results
    m = manifest_results["sample.root"]
    assert m["exists"] is True
    assert m["match"] is True
