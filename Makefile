# Makefile for HGRF — high-level pipeline commands
# Usage: make help
CONDA_ENV ?= hgrf_core
PYTHON := conda run -n $(CONDA_ENV) python
PIP := conda run -n $(CONDA_ENV) pip
NBEXEC := jupyter nbconvert --to html --execute --ExecutePreprocessor.timeout=600

# Paths
ROOT_SAMPLE ?= data/raw/$(shell ls data/raw/*.root 2>/dev/null | head -n1)
PREPROC_EVENT_OUT := results/preprocessed_event.parquet
PREPROC_PART_OUT := results/preprocessed_particles.parquet
ANGLES_SUM := results/angles_summary.csv
STATS_OUT := results/stats_results.json

.PHONY: help env docker build-docker download-sample download-jpl preprocess-event preprocess-particle analysis stats notebooks clean

help:
	@echo "Makefile targets for HGRF"
	@echo "  make env             -> create conda env from environment.yml (uses mamba/conda)"
	@echo "  make docker          -> build Docker image (CPU)"
	@echo "  make download-sample URL=<url>  -> download sample ROOT into data/raw/"
	@echo "  make download-jpl TARGET=399 START=2025-01-01 STOP=2025-12-31 STEP='1 d'"
	@echo "  make preprocess-event INPUT=$(ROOT_SAMPLE)  -> per-event preprocessing (parquet)"
	@echo "  make preprocess-particle INPUT=$(ROOT_SAMPLE) -> per-particle table (parquet)"
	@echo "  make analysis INPUT=$(PREPROC_PART_OUT) -> compute angles (OUTPUT=$(ANGLES_SUM))"
	@echo "  make stats INPUT=$(ANGLES_SUM) -> run statistical pipeline (output $(STATS_OUT))"
	@echo "  make notebooks       -> execute notebooks (01,02,03) to HTML"
	@echo "  make clean           -> remove transient files (results/* tmp_*)"

env:
	@echo "Creating conda environment '$(CONDA_ENV)' from environment.yml (may require mamba/conda)..."
	@if command -v mamba >/dev/null 2>&1; then \
	  mamba env create -f environment.yml -n $(CONDA_ENV) || true; \
	else \
	  conda env create -f environment.yml -n $(CONDA_ENV) || true; \
	fi
	@echo "Environment created. Use: conda activate $(CONDA_ENV)"

docker:
	@echo "Build Docker image hgrf:latest (CPU)."
	DOCKER_BUILDKIT=0 docker build -t hgrf:latest .

download-sample:
	@if [ -z "$(URL)" ]; then \
	  echo "Usage: make download-sample URL=<url>"; exit 1; \
	fi
	@mkdir -p data/raw
	@./scripts/download_cern_sample.sh "$(URL)"

download-jpl:
	@if [ -z "$(TARGET)" ]; then \
	  echo "Usage: make download-jpl TARGET=399 START=2025-01-01 STOP=2025-12-31 STEP='1 d'"; exit 1; \
	fi
	@mkdir -p data/raw
	@./scripts/download_jpl_ephem.sh "$(TARGET)" "$(START)" "$(STOP)" "$(STEP)"

preprocess-event:
	@echo "Preprocessing (per_event) from $(INPUT)"
	@mkdir -p results
	$(PYTHON) src/data_preprocessing.py --input "$(INPUT)" --mode per_event --output "$(PREPROC_EVENT_OUT)" --force || true
	@echo "Wrote $(PREPROC_EVENT_OUT)"

preprocess-particle:
	@echo "Preprocessing (per_particle) from $(INPUT)"
	@mkdir -p results
	$(PYTHON) src/data_preprocessing.py --input "$(INPUT)" --mode per_particle --output "$(PREPROC_PART_OUT)" --force || true
	@echo "Wrote $(PREPROC_PART_OUT)"

analysis:
	@echo "Running analysis (angles) using input: $(INPUT)"
	@mkdir -p results
	$(PYTHON) src/analysis.py --input "$(INPUT)" --input-format parquet --output "$(ANGLES_SUM)" || true
	@echo "Wrote $(ANGLES_SUM)"

stats:
	@echo "Running statistical analysis on $(INPUT)"
	@mkdir -p results
	$(PYTHON) src/stats.py --input "$(INPUT)" --column mean_angle_deg --output "$(STATS_OUT)" || true
	@echo "Wrote $(STATS_OUT)"

notebooks:
	@echo "Executing notebooks (01, 02, 03) to HTML..."
	@mkdir -p results
	$(NBEXEC) notebooks/01_data_inspection.ipynb --output notebooks/01_data_inspection.html || true
	$(NBEXEC) notebooks/02_selection_and_angles.ipynb --output notebooks/02_selection_and_angles.html || true
	$(NBEXEC) notebooks/03_statistical_tests.ipynb --output notebooks/03_statistical_tests.html || true
	@echo "Notebooks rendered to HTML in notebooks/"

clean:
	@echo "Cleaning results and temporary files..."
	@rm -rf results/* tmp_* notebooks/*.html || true
	@echo "Done."
