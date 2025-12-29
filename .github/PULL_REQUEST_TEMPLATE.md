# Pull Request Template

## Descripción
- Resumen breve de los cambios:
- Issue asociado: # (si aplica)

## Tipo de cambio
- [ ] Bugfix
- [ ] Nueva funcionalidad
- [ ] Documentación
- [ ] Infra / CI / Docker

## Pasos para reproducir / comprobar
- Comandos para reproducir los resultados localmente:
  ```
  make env
  make preprocess-particle INPUT=data/raw/mi_sample.root
  make analysis INPUT=results/preprocessed_particles.parquet
  ```

## Tests y calidad
- [ ] Añadí tests (pytest) o notebooks de ejemplo
- [ ] `flake8` y `black` ejecutados
- [ ] Notebooks ejecutados con nbconvert (si aplica)

## Provenance / reproducibilidad
- Commit SHA de referencia:
- Datos usados (manifest / .sha256):
- Seed aleatorio (si aplica):

## Checklist
- [ ] He seguido CONTRIBUTING.md
- [ ] No hay datos sensibles ni credenciales en el PR
- [ ] Añadí documentación/CHANGELOG si necesario

## Firma humana responsable
- Nombre y correo (persona que valida científicamente):
