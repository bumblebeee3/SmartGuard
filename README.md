# SmartGuard

SmartGuard es un **prototipo académico de análisis heurístico de contratos inteligentes Solidity** desarrollado por el Grupo 7 de Ingeniería Civil Telemática de la UTFSM.

La aplicación recibe código Solidity, ejecuta un conjunto acotado de reglas de revisión y muestra hallazgos con severidad, ubicación aproximada, fragmento de código, explicación y recomendación.

> **Importante:** SmartGuard no confirma que un contrato sea vulnerable ni garantiza que sea seguro. Es una herramienta educativa de apoyo a una revisión inicial y no reemplaza una auditoría profesional.

## Contexto

El desafío se relaciona con la experiencia de Gonzalo Sánchez Vargas, exalumno UTFSM con trayectoria en desarrollo de software, auditoría de Smart Contracts y desarrollo de Smart Contracts.

## Estado actual — v0.2

Esta versión ya cuenta con una aplicación web funcional, API, motor de reglas ampliado, carga de archivos `.sol`, ejemplos integrados, resumen por severidad, reporte JSON y pruebas automatizadas.

### Reglas implementadas

| ID | Regla | Severidad |
|---|---|---|
| SG001 | Versión antigua de Solidity | Baja |
| SG002 | Uso de `tx.origin` | Media |
| SG003 | Uso de `selfdestruct` | Media |
| SG004 | Posible patrón de reentrancy | Alta |
| SG005 | Llamada de bajo nivel sin verificar | Media |
| SG006 | Uso de `delegatecall` | Media |
| SG007 | Dependencia temporal con `block.timestamp` | Baja |
| SG008 | Aleatoriedad basada en variables de bloque | Media |

Las reglas son heurísticas y pueden producir falsos positivos o falsos negativos.

## Flujo de funcionamiento

```text
Usuario
  ↓
Pega código o carga archivo .sol
  ↓
Frontend HTML/CSS/JavaScript
  ↓
API FastAPI
  ↓
Analizador Python
  ↓
8 reglas heurísticas
  ↓
Hallazgos + severidad + fragmento + recomendación
  ↓
Reporte visual / descarga JSON
```

## Funcionalidades

- Pegar código Solidity directamente en la interfaz.
- Cargar un archivo `.sol` desde el equipo.
- Cargar ejemplos vulnerable y más seguro con un clic.
- Ejecutar 8 reglas heurísticas de revisión.
- Mostrar conteo de hallazgos por severidad.
- Mostrar función y línea aproximada asociada al hallazgo.
- Mostrar el fragmento de código detectado.
- Descargar el resultado como reporte JSON.
- Consultar el catálogo de reglas mediante la API.
- Ejecutar pruebas automáticas localmente o mediante GitHub Actions.

## Tecnologías

- Python 3.11+
- FastAPI
- Uvicorn
- HTML
- CSS
- JavaScript
- Solidity como lenguaje analizado

## Estructura

```text
smartguard/
├── .github/workflows/tests.yml
├── app/
│   ├── analyzer.py
│   ├── main.py
│   └── static/
│       ├── index.html
│       ├── script.js
│       └── style.css
├── docs/
│   └── mensaje_cierre_gonzalo.md
├── samples/
│   ├── vulnerable.sol
│   └── safer.sol
├── tests/
│   └── test_analyzer.py
├── CHANGELOG.md
├── requirements.txt
└── README.md
```

## Instalación

### Windows PowerShell

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
```

## Ejecutar la aplicación

```powershell
python -m uvicorn app.main:app --reload
```

Abrir:

```text
http://127.0.0.1:8000
```

## Ejecutar pruebas

```powershell
python -m unittest discover -s tests -v
```

La versión 0.2 incluye **12 pruebas automáticas**.

## API

### `POST /api/analyze`
Analiza código Solidity.

### `GET /api/rules`
Entrega las reglas activas.

### `GET /api/sample/vulnerable`
Entrega el caso de prueba vulnerable.

### `GET /api/sample/safer`
Entrega el caso de prueba más seguro.

### `GET /api/health`
Entrega estado, versión y cantidad de reglas activas.

## Limitaciones

SmartGuard no ejecuta el contrato, no lo despliega en una blockchain y no realiza análisis formal del comportamiento completo. El motor se basa en patrones heurísticos y relaciones simples entre líneas.

Por lo tanto:

- un hallazgo no confirma por sí solo una vulnerabilidad explotable;
- la ausencia de hallazgos no garantiza seguridad;
- aún pueden existir falsos positivos y falsos negativos;
- el prototipo no reemplaza herramientas especializadas ni una auditoría humana.

## Trabajo pendiente

- Mejorar el análisis estructural de funciones y variables.
- Reducir falsos positivos de reglas contextuales.
- Agregar más contratos de validación.
- Evaluar análisis mediante AST en una siguiente etapa.
- Agregar exportación de informe visual además de JSON.
- Validar resultados con retroalimentación del exalumno.

## Equipo

**Grupo 7 – Ingeniería Civil Telemática, UTFSM**

- Bastian Torres
- Nicole Zúñiga

## Evidencias incluidas

El repositorio incluye material de validación en `docs/evidencias/`:

- `caso_vulnerable.png` — demostración con 7 hallazgos.
- `caso_mas_seguro.png` — demostración sin coincidencias en las reglas configuradas.
- `pruebas_automaticas.txt` — salida de la suite de 12 pruebas.
- `resultados_validacion.md` — resumen de los casos de demostración.
- `arquitectura.md` — descripción de la arquitectura actual.
