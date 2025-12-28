# CONTRIBUTING.md — Cómo contribuir a HGRF

Gracias por querer contribuir. Este documento describe el flujo recomendado para colaborar de forma ordenada y reproducible.

1) Cómo empezar
- Clona este repo y crea una rama para tu cambio:
  ```
  git clone <REPO_URL>
  cd HARMONIC-GRAVITON-Reproducible-Research-Framework-HGRF-
  git checkout -b feat/mi-cambio
  ```
- Prepárate un entorno reproducible:
  - Recomendado: Miniforge/conda
    ```
    mamba env create -f environment.yml -n hgrf_core
    conda activate hgrf_core
    ```
  - Alternativa: Docker (`make docker`).

2) Issues
- Antes de trabajar en una característica grande, abre un issue describiendo:
  - objetivo, datos de entrada, outputs esperados, y recursos computacionales necesarios.
- Usa etiquetas (bug, enhancement, docs, help-wanted).

3) Pull Requests
- Crea PRs contra la rama `main`. Incluye:
  - Descripción clara del cambio.
  - Cómo reproducir los resultados (comandos).
  - Tests o notebooks que demuestran la funcionalidad.
  - Firma y afiliación del autor humano que valida el cambio.
- Usamos revisión por pares: al menos una aprobación humana antes de merge.

4) Formato de código y pruebas
- Python: sigue PEP8. Usa `black` y `flake8`.
  ```
  black src/ notebooks/ --line-length 120
  flake8 src/
  ```
- Tests: añade tests en `tests/` y usa `pytest`. El CI ejecuta pruebas básicas y smoke tests.

5) Notebooks
- Mantén notebooks reproducibles: no incluyas credenciales ni archivos grandes.
- Para outputs reproducibles usa `nbconvert` en CI y guarda HTML resultante en `notebooks/*.html` cuando sea necesario.
- Si modificas un notebook, añade una celda con `# provenance` que indique:
  - commit SHA, seed aleatorio, entorno (output of `conda list --explicit`).

6) Datos y privacidad
- No subir datos sensibles. Usa `data/raw/README.md` y `manifest.json` para describir datasets.
- Para grandes archivos, añade `.sha256` en `data/raw/` y guías para descargar.

7) Firmas y autoría
- Cada PR debe indicar claramente los autores humanos que validan científicamente los cambios. ChatGPT u otras IAs pueden aparecer en el cuerpo del PR como asistente técnico, pero la autoría y responsabilidad científica recae en humanos.

8) Política ética y límites
- No se aceptarán contribuciones que:
  - proporcionen instrucciones para realizar intervenciones biomédicas peligrosas;
  - faciliten actividades ilegales, maliciosas o que pongan en riesgo a personas o animales.
- Para investigaciones con riesgo bioético, se requiere aprobación institucional y documentación clara.

9) Licencia y citación
- Este proyecto usa Apache-2.0. Añade `CITATION.bib` si publicas resultados y cita el repositorio según el formato en README.

10) Contacto
- Para consultas mayores, abre un issue o contacta a: Maestro Benjamín (github.com/MechMind-dwv)

Gracias por colaborar — cada contribución mejora la reproducibilidad y la calidad científica del proyecto.
