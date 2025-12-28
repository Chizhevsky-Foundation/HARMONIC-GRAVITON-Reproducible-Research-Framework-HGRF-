# Dockerfile para HGRF (entorno reproducible, CPU)
FROM continuumio/miniconda3:23.11.1

# Evitar prompts de conda
ENV PATH /opt/conda/bin:$PATH
SHELL ["/bin/bash", "-lc"]

# Copiar environment y crear el entorno
WORKDIR /opt/hgrf
COPY environment.yml /opt/hgrf/environment.yml

RUN conda update -n base -c defaults conda -y && \
    conda env create -f /opt/hgrf/environment.yml && \
    conda clean -afy

# Make RUN commands use the new environment:
ENV CONDA_DEFAULT_ENV=hgrf
ENV PATH /opt/conda/envs/hgrf/bin:$PATH

# Crear un usuario no-root opcional (mejor práctica)
RUN useradd -m hgrfuser && chown -R hgrfuser:hgrfuser /opt/hgrf
USER hgrfuser
WORKDIR /home/hgrfuser

# Entrypoint por defecto: bash (útil para interactuar)
ENTRYPOINT ["/bin/bash"]
