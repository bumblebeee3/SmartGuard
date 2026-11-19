# Arquitectura de SmartGuard v0.2

```text
Usuario
  │
  ├── pega código / carga archivo .sol
  ▼
Frontend
HTML + CSS + JavaScript
  │
  │ POST /api/analyze
  ▼
FastAPI
  │
  ▼
SmartContractAnalyzer (Python)
  │
  ├── SG001 ... SG008
  ▼
Resultado JSON
  │
  ▼
Interfaz
hallazgos + severidad + línea + función + fragmento + recomendación
```

## Responsabilidades

### Frontend
- Captura código Solidity.
- Permite cargar archivos `.sol`.
- Carga casos de prueba.
- Muestra métricas y hallazgos.
- Descarga el resultado como JSON.

### API
- Valida la entrada.
- Expone catálogo de reglas y casos de ejemplo.
- Ejecuta el analizador.
- Resume hallazgos por severidad.

### Analizador
- Elimina comentarios conservando las líneas originales.
- Identifica contexto aproximado de función.
- Ejecuta ocho reglas heurísticas.
- Ordena hallazgos por severidad.
