# data/raw/README.md
Instrucciones para añadir datasets y registrar procedencia (provenance)
Autor responsable: Benjamin Cabeza Durán
Proyecto: HARMONIC‑GRAVITON — HGRF
Fecha: 2025-12-28

Propósito
--------
Esta carpeta contiene enlaces simbólicos o muestras pequeñas (small samples) de los archivos RAW usados para el desarrollo. **Nunca** subir archivos de gran tamaño (p. ej. datasets de ~TB) directamente al repositorio. En su lugar, guarde metadatos, hashes y scripts para descargar o montar los datos.

Estructura recomendada
----------------------
- data/raw/                  # carpeta en el repo (solo enlaces, muestras y metadatos)
  - sample_small.root        # OPTIONAL: ejemplos pequeños (<100 MB) para pruebas
  - my_large_file.root.sha256 # archivo hash para un dataset grande ubicado fuera del repo
  - manifest.json            # (recomendado) lista con metadatos de los archivos raw
  - README.md                # este archivo

Reglas y buenas prácticas
-------------------------
1. No subir archivos grandes al repo. Si el dataset es grande:
   - Mantén el archivo en almacenamiento externo (NFS, object storage, servidor institucional) o comparte un enlace directo (p.ej. CERN OpenData, S3, HTTP).
   - Añade en data/raw/ únicamente:
     - un archivo `.sha256` con el hash del archivo,
     - opcionalmente un `symlink` a la ubicación local (si se trabaja en la misma máquina),
     - un `manifest.json` con metadatos y la URL de descarga.

2. Cómo guardar un hash SHA256:
   - Genera el hash en la máquina donde reside el archivo (no en el repo si el archivo es grande).
     ```
     sha256sum /ruta/al/archivo.root > archivo.root.sha256
     ```
   - Coloca `archivo.root.sha256` en `data/raw/` y registra en `manifest.json` la URL y la fecha de creación.

3. Ejemplo de `manifest.json` (recomendado)
   - Formato JSON con una entrada por archivo:
     {
       "files": [
         {
           "filename": "my_run_sample.root",
           "sha256": "abcdef1234...",
           "size_bytes": 12345678,
           "source_url": "https://opendata.cern.ch/record/xxxxx/files/my_run_sample.root",
           "date_downloaded": "2025-12-28T18:00:00Z",
           "notes": "Small sample for rapid testing"
         }
       ]
     }
   - Guarda `manifest.json` en `data/raw/manifest.json`. Esto facilita la reproducibilidad y la verificación por terceros.

4. Symlinks vs copia
   - Si trabajas en la misma máquina y no quieres duplicar espacio, crea symlinks:
     ```
     ln -s "/ruta/real/al/archivo.root" data/raw/archivo.root
     ```
   - Git registrará el symlink (no el contenido). Asegúrate de documentar la ruta real en `manifest.json` o README.

5. Verificación de integridad (comandos de uso)
   - Verificar un hash SHA256:
     ```
     sha256sum -c data/raw/archivo.root.sha256
     ```
     Debe responder `archivo.root: OK`.
   - Si tienes `manifest.json`, verifica todos los hashes mediante un script (ejemplo en src/).

6. Acceso remoto / streaming
   - Para archivos enormes puedes usar xrootd, http(s) o s3. Guarda la URL y las credenciales necesarias fuera del repo (no en texto plano).  
   - Ejemplo de lectura por streaming con uproot (si está disponible):
     ```python
     import uproot
     f = uproot.open("root://server.example.org//path/to/file.root")
     ```

7. Versionado y provenance
   - Cada vez que añadas o actualices un archivo en data/raw/, actualiza `manifest.json` y añade una entrada `provenance` en la salida de tus scripts (sha256, comando de descarga, fecha, commit SHA del repo).
   - Registra en commits del repo el `manifest.json` y los `.sha256` (no los datasets).

8. Ignorar archivos grandes
   - Asegúrate de que `.gitignore` incluya patrones para no subir accidentalmente archivos grandes, por ejemplo:
     ```
     /data/raw/*.root
     /data/raw/*.root.gz
     /data/raw/*.root.*  # otros derivados binarios
     ```

9. Ejemplo rápido — flujo recomendado
   - En la máquina de datos:
     ```
     # generar SHA256
     sha256sum /mnt/storage/runA.root > runA.root.sha256
     # crear manifest o actualizarlo
     # crear symlink (opcional)
     ln -s /mnt/storage/runA.root /path/to/repo/data/raw/runA.root
     # luego en la máquina de trabajo (local repo)
     git add data/raw/runA.root.sha256 data/raw/manifest.json
     git commit -m "Add metadata for runA (sha256 + manifest)"
     git push origin main
     ```

10. Seguridad y privacidad
    - No subas credenciales ni datos sensibles. Si un dataset requiere autorización, documenta el proceso de obtención y no incluyas tokens en el repo.

Contacto / firmas
-----------------
Responsable de este documento:
- Benjamin Cabeza Durán — Fundación Chizhevsky

Para dudas sobre cómo añadir datos o si quieres que prepare scripts automáticos para verificar `manifest.json` y hashes, abre un issue en:
https://github.com/Chizhevsky-Foundation/FTRT-Scientific-Validation/issues

