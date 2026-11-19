# Changelog

## 0.2.0

- Se amplió el motor de 4 a 8 reglas heurísticas.
- Se agregó detección de llamadas de bajo nivel sin verificar, `delegatecall`, dependencia temporal y aleatoriedad basada en variables de bloque.
- El analizador ahora ignora comentarios simples y conserva contexto de función.
- Cada hallazgo incluye categoría, función y fragmento de código.
- Se agregó carga local de archivos `.sol`.
- Se agregaron botones para cargar ejemplos vulnerable y más seguro.
- Se agregó resumen por severidad y nivel de revisión.
- Se agregó descarga del reporte en JSON.
- Se agregó catálogo visual de reglas activas.
- Se aumentaron las pruebas automáticas a 12.
- Se agregó workflow de GitHub Actions para ejecutar pruebas en push y pull requests.
