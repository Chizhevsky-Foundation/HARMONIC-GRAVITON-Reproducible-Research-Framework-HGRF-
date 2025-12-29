# Dockerfile reproducible (CPU) para HGRF — usa mambaforge y pip para paquetes PyPI no disponibles en conda
FROM condaforge/mambaforge:latest

SHELL ["/bin/bash", "-lc"]
WORKDIR /opt/hgrf

# Copiar environment
COPY environment.yml /opt/hgrf/environment.yml

# Crear env base con mamba pero sin instalar paquetes pip-only
# We'll create the env and then pip-install uproot/awkward/etc.
RUN mamba env create -f /opt/hgrf/environment.yml -n hgrf --no-pin || true && \
    /opt/conda/envs/hgrf/bin/python -m pip install --upgrade pip setuptools wheel && \
    # install packages that may be only available in PyPI
    /opt/conda/envs/hgrf/bin/python -m pip install "uproot" "awkward" && \
    mamba clean --all --yes

ENV CONDA_DEFAULT_ENV=hgrf
ENV PATH=/opt/conda/envs/hgrf/bin:$PATH

# Crear usuario no-root
RUN useradd -m hgrfuser && chown -R hgrfuser /opt/hgrf
USER hgrfuser
WORKDIR /home/hgrfuser

ENTRYPOINT ["/bin/bash"]
