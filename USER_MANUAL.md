# Manual de Usuario — HARMONIC‑GRAVITON (HGRF)

Última revisión: 2025-12-29  
Autores: Benjamin Cabeza Durán (dirección científica) / ChatGPT (implementación técnica)

Índice
------
- Resumen del proyecto
- Requisitos previos
- Instalación del entorno
- Uso rápido (Quickstart)
- Descripción de scripts y notebooks
- Flujo reproducible paso a paso
- Gestión de datos y manifest/.sha256
- Verificación automática (verify_manifest.py)
- Ejecución en Docker
- CI / GitHub Actions (smoke tests)
- Solución de problemas comunes
- Buenas prácticas y gobernanza/ética
- Contribuir y citar el proyecto
- Contacto

Resumen del proyecto
--------------------
HGRF es un marco reproducible para investigar correlaciones entre métricas heliocéntricas (FTRT) y datos de colisionadores (LHC Open Data). El repo contiene código, notebooks y scripts que permiten descargar muestras, preprocesar ROOT (NanoAOD), calcular métricas (ángulos entre partículas), y ejecutar pruebas estadísticas reproducibles.

Requisitos previos
------------------
- Sistema Linux / WSL o macOS (se recomienda Linux para compatibilidad).
- Git instalado.
- Miniforge / Conda (se recomienda Miniforge/Miniconda/Miniforge3).
- Docker (opcional, para ejecución contenedorizada).
- Espacio en disco para samples (no hace falta tener TB localmente para desarrollo: usar muestras pequeñas o symlinks).

Instalación del entorno
-----------------------
1. Clonar repo:
   git clone https://github.com/Chizhevsky-Foundation/HARMONIC-GRAVITON-Reproducible-Research-Framework-HGRF-.git
   cd HARMONIC-GRAVITON-Reproducible-Research-Framework-HGRF-

2. Crear entorno con conda/mamba (recomendado):
   make env
   # o manual:
   conda env create -f environment.yml -n hgrf_core
   conda activate hgrf_core

3. (Opcional) Si vas a usar Docker (imagen CPU):
   make docker
   # o
   DOCKER_BUILDKIT=0 docker build -t hgrf:latest .

Uso rápido (Quickstart)
-----------------------
Flujo mínimo reproducible (asumiendo un sample ROOT accesible o symlink en `data/raw/`):

1. Verificar archivos en data/raw:
   ls -l data/raw

2. Preprocesar por partícula:
   make preprocess-particle INPUT=data/raw/tu_sample.root

3. Calcular ángulos:
   make analysis INPUT=results/preprocessed_particles.parquet

4. Ejecutar pruebas estadísticas:
   make stats INPUT=results/angles_summary.csv

5. Renderizar notebooks:
   make notebooks

Para ejecutar todo en secuencia (orquestador):
   ./run_all.sh "URL_DEL_SAMPLE_OPCIONAL" 200000
(El segundo argumento es entry_stop opcional.)

Descripción de scripts y notebooks
----------------------------------
- environment.yml / Dockerfile: entorno reproducible.
- .github/workflows/ci.yml: CI smoke tests que instalan el entorno e importan librerías.
- scripts/download_cern_sample.sh: descarga archivos ROOT (usa links directos).
- scripts/download_jpl_ephem.sh: wrapper para JPL Horizons (astroquery).
- scripts/inspect_root.py: inspección rápida de un ROOT (ramas, trees).
- src/data_preprocessing.py: lectura con uproot/awkward → tablas per_event / per_particle.
- notebooks/01_data_inspection.ipynb: inspección interactiva del sample.
- notebooks/02_selection_and_angles.ipynb: selección de muones y cálculo de ángulos.
- notebooks/03_statistical_tests.ipynb: bootstrap, permutación y surrogates.
- src/analysis.py: cálculo vectorial de ángulos y resumen por evento.
- src/stats.py: MLE gaussiano, bootstrap y toy‑MC.
- src/verify_manifest.py: verifica .sha256 y manifest.json en data/raw.
- Makefile / run_all.sh: orquestación de pipeline.
- config/selection.yaml: parámetros de corte (pt_min, eta, triggers).

Flujo reproducible (paso a paso con comandos)
---------------------------------------------
1. Preparar datos (usar symlink para no duplicar):
   ln -s "/ruta/real/mifile.root" data/raw/mifile.root

2. Generar hashes y manifest:
   sha256sum "/ruta/real/mifile.root" > data/raw/mifile.root.sha256
   python - <<PY
   # (script para añadir entrada a data/raw/manifest.json)
   PY

3. Verificar manifest:
   conda activate hgrf_core
   python src/verify_manifest.py --verbose

4. Preprocesado:
   conda run -n hgrf_core python src/data_preprocessing.py --input data/raw/mifile.root --mode per_particle --output results/preprocessed_particles.parquet --force

5. Análisis angular:
   conda run -n hgrf_core python src/analysis.py --input results/preprocessed_particles.parquet --input-format parquet --output results/angles_summary.csv

6. Estadística:
   conda run -n hgrf_core python src/stats.py --input results/angles_summary.csv --column mean_angle_deg --output results/stats_results.json

7. Renderizar notebooks:
   conda run -n hgrf_core jupyter nbconvert --to html --execute notebooks/01_data_inspection.ipynb --output notebooks/01_data_inspection.html

Gestión de datos y manifest/.sha256
----------------------------------
- Nunca subir datasets grandes al repo. Mantén `data/raw/` con symlinks, `.sha256` y `manifest.json`.
- Para añadir un dataset:
  1. Guarda el archivo en almacenamiento (NFS/S3/...).
  2. Crea un symlink en data/raw que apunte al archivo.
  3. Genera el .sha256 y actualiza manifest.json con filename, sha256 y size_bytes.
- Verifica con:
  python src/verify_manifest.py --verbose
  Resultado OK esperado: "All checked items OK."

Ejecución en Docker
-------------------
- Construir imagen:
  DOCKER_BUILDKIT=0 docker build -t hgrf:latest .
- Ejecutar contenedor (monta repo y data):
  docker run --rm -it -v $(pwd):/workspace -w /workspace hgrf:latest /bin/bash
- Dentro del contenedor puedes ejecutar los mismos comandos Python.

CI / GitHub Actions
-------------------
- El workflow .github/workflows/ci.yml realiza tests ligeros (crea env, importa librerías).
- Evita ejecutar análisis pesados en CI (use samples pequeños).
- Si añades manifest/.sha256 la Action puede ejecutar verify_manifest como un check opcional.

Solución de problemas comunes
-----------------------------
- `conda: command not found` → instala Miniforge/Miniconda y reabre la shell.
- `pip: externally-managed-environment` → crea un virtualenv o usa conda.
- `Docker BuildKit` error → construir con DOCKER_BUILDKIT=0.
- `Notebook does not appear to be JSON` → sobrescribir notebook con nbformat (ya incluido en repo).
- `verify_manifest.py` reporta mismatch → re-apuntar symlink o regenerar .sha256; luego ejecutar verify_manifest.
- `jupyter-lab not found` → instalar jupyterlab en el entorno conda.

Buenas prácticas y gobernanza / ética
------------------------------------
- Sigue CODE_OF_CONDUCT.md y CORPORATE_ETHICS_POLICY.md.
- No difundir procedimientos biomédicos no regulados o peligrosos.
- Antes de publicar afirmaciones extraordinarias: registrar provenance, documentar sistemáticas y buscar réplica externa.

Contribuir y pull requests
--------------------------
- Lee CONTRIBUTING.md para normas: PRs, tests, firma humana responsable.
- Usa ramas feature/*, describe cambios en el PR y añade tests/notebooks de validación.
- Incluye provenance (hashes, commit SHA, seed) en notebooks y reportes.

Citar el proyecto
-----------------
Añade la entrada de CITATION.bib al citar el software / data. Actualiza la nota con commit SHA si refieres esta versión.

Contacto
--------
- Repo: https://github.com/Chizhevsky-Foundation/HARMONIC-GRAVITON-Reproducible-Research-Framework-HGRF-
- Responsable del proyecto: Benjamin Cabeza Durán — github.com/MechMind-dwv  
- Reportes (ética / confidencial): ia.mechmind@gmail.com

Anexos y recursos
-----------------
- Listado de archivos clave: README.md, CITATION.bib, docs/methodology.md, config/selection.yaml, Makefile, run_all.sh.
- Scripts de utilidad: src/verify_manifest.py, scripts/download_cern_sample.sh, scripts/download_jpl_ephem.sh.

Fin del Manual
--------------
