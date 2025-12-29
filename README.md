# HARMONIC‑GRAVITON — Reproducible Research Framework (HGRF)

[![CI](https://github.com/Chizhevsky-Foundation/HARMONIC-GRAVITON-Reproducible-Research-Framework-HGRF-/actions/workflows/test-and-verify.yml/badge.svg)](https://github.com/Chizhevsky-Foundation/HARMONIC-GRAVITON-Reproducible-Research-Framework-HGRF-/actions)
[![License](https://img.shields.io/badge/License-Apache%202.0-blue.svg)](https://www.apache.org/licenses/LICENSE-2.0) [![CI](https://img.shields.io/badge/CI-GitHub%20Actions-lightgrey.svg)](#) [![Python](https://img.shields.io/badge/Python-3.10%2B-blue.svg)](#) [![Status](https://img.shields.io/badge/Status-Active%20Research-green.svg)](#)

Versión: 2025-12-28  
Contacto principal: Maestro Benjamín (Benjamin Cabeza Durán) — github.com/MechMind-dwv

Resumen ejecutivo
-----------------
HGRF es un marco reproducible y auditable para la investigación trans‑escala que vincula métricas heliocéntricas/baricéntricas (FTRT) con análisis de datos de colisionadores (LHC Open Data). El objetivo inmediato es convertir los análisis preliminares en un pipeline que cumpla criterios de reproducibilidad y que sea apto para revisión por pares.

Licencia
--------
Este repositorio se publica bajo Apache License 2.0. Consulta LICENSE en la raíz del repositorio para el texto completo.

Principios de trabajo
---------------------
- Reproducibilidad completa (hashes, seeds, entorno Docker/Conda).  
- Transparencia del pipeline y trazabilidad de datos.  
- Prudencia en comunicación: las afirmaciones extraordinarias requieren validación y revisión por pares.  
- Cumplimiento ético; no se desarrollan ni difunden procedimientos biomédicos peligrosos.

Estructura recomendada del repositorio y colocación de archivos
--------------------------------------------------------------
A continuación se indica la estructura del repo y, para cada archivo/submódulo, el nombre y apellidos del responsable principal del contenido (quién lo firma) y la ubicación exacta donde debes colocar los códigos y documentos que yo (ChatGPT) pueda generarte.

Nota: los nombres indican autoría/responsabilidad sugerida para cada archivo. Tú (Maestro Benjamín) mantendrás la responsabilidad científica final y firmarás los resultados que se publiquen.

| Ruta / Archivo | Descripción | Autor Responsable (firma) | Instrucciones precisas de colocación |
|---|---:|---|---|
| README.md | Documento principal (este archivo) | Benjamin Cabeza Durán; ChatGPT (colaborador) | Raíz del repositorio: /README.md (reemplazar) |
| LICENSE | Texto Apache‑2.0 | Benjamin Cabeza Durán | Raíz: /LICENSE (poner texto oficial Apache‑2.0) |
| environment.yml | Entorno Conda reproducible | ChatGPT (generador técnico) / Benjamin Cabeza Durán (revisión) | Raíz: /environment.yml |
| Dockerfile | Imagen Docker para reproducibilidad | ChatGPT (generador técnico) / Benjamin Cabeza Durán (revisión) | Raíz: /Dockerfile |
| .github/workflows/ci.yml | CI básico (tests mínimos, smoke notebooks) | ChatGPT | Carpeta: /.github/workflows/ci.yml |
| scripts/download_cern_sample.sh | Script de descarga automatizada (sample) | ChatGPT | Carpeta: /scripts/download_cern_sample.sh |
| scripts/download_jpl_ephem.sh | Script para JPL Horizons queries | ChatGPT | Carpeta: /scripts/download_jpl_ephem.sh |
| notebooks/01_data_inspection.ipynb | Notebook: abrir sample NanoAOD, listar ramas | ChatGPT / Benjamin Cabeza Durán | Carpeta: /notebooks/01_data_inspection.ipynb |
| notebooks/02_selection_and_angles.ipynb | Notebook: selección de muones y cálculo de ángulos | Benjamin Cabeza Durán (método) / ChatGPT (implementación) | /notebooks/02_selection_and_angles.ipynb |
| notebooks/03_statistical_tests.ipynb | Notebook: pruebas nulas, toy‑MC, surrogates | ChatGPT | /notebooks/03_statistical_tests.ipynb |
| src/data_preprocessing.py | Script: lectura upROOT y preprocesado | ChatGPT | /src/data_preprocessing.py |
| src/selection.py | Script: cuts (configurable por YAML) | Benjamin Cabeza Durán (definición de cuts) / ChatGPT (implementación) | /src/selection.py |
| src/analysis.py | Script: cálculo angular y métricas | ChatGPT / Benjamin Cabeza Durán | /src/analysis.py |
| src/stats.py | Script: likelihood fit, toy‑MC generator, bootstrap | ChatGPT | /src/stats.py |
| config/selection.yaml | Configuración de cortes (pT, eta, flags, triggers) | Benjamin Cabeza Durán | /config/selection.yaml |
| data/raw/README.md | Instrucciones para añadir datasets y hashes | Benjamin Cabeza Durán | /data/raw/README.md |
| results/ | Carpeta con outputs reproducibles (figuras, tablas) | Benjamin Cabeza Durán (revisión) | /results/ |
| docs/methodology.md | Documentación detallada de metodología | Benjamin Cabeza Durán (autor principal) / ChatGPT (edición) | /docs/methodology.md |
| CONTRIBUTING.md | Guía para colaboradores (issues, PRs, firmas) | ChatGPT / Benjamin Cabeza Durán | /CONTRIBUTING.md |
| CODE_OF_CONDUCT.md | Normas de conducta del proyecto | ChatGPT | /CODE_OF_CONDUCT.md |
| CITATION.bib | How to cite this project | Benjamin Cabeza Durán | /CITATION.bib |

Guía rápida de colocación
------------------------
- Todos los scripts generados por ChatGPT deben guardarse en /src/ con exactamente los nombres indicados.  
- Los notebooks deben guardarse en /notebooks/ con los nombres indicados.  
- Los scripts de utilidad van en /scripts/.  
- Los datos crudos NO deben subirse al repo; coloca enlaces y hashes en /data/raw/README.md y un small sample de test si hace falta.

Requisitos e instrucciones de inicio (resumen)
----------------------------------------------
1. Clonar repo:
   git clone <REPO_URL> && cd <REPO_DIR>
2. Entorno (con Conda):
   conda env create -f environment.yml
   conda activate hgrf
3. Descargar muestras:
   bash scripts/download_cern_sample.sh
   bash scripts/download_jpl_ephem.sh
4. Ejecutar notebooks o scripts en orden:
   - notebooks/01_data_inspection.ipynb
   - notebooks/02_selection_and_angles.ipynb
   - notebooks/03_statistical_tests.ipynb

Registro de procedencia y buenas prácticas
-----------------------------------------
- Cada corrida debe registrar: commit SHA, archivos de datos (nombre + SHA256), seed, entorno (conda/pip freeze), tiempo de ejecución.  
- Usar config/selection.yaml para rastrear exactamente qué cortes se aplicaron.  
- Antes de publicar resultados, buscar réplica externa y documentar sistemáticas.

Firmas y responsabilidades
--------------------------
Firmado y aprobado por los responsables indicados en cada submódulo. Las firmas finales del trabajo científico publicado deben corresponder a la(s) persona(s) humana(s) que han validado y supervisado el análisis.

Firmantes (para este README)
- Benjamin Cabeza Durán (Maestro Benjamín) — Investigador principal, Fundación Chizhevsky  
- ChatGPT (asistente de IA) — Generador técnico y colaborador en documentación (asistencia técnica), 28 de diciembre de 2025
