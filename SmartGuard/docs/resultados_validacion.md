# Resultados de validación — SmartGuard v0.2

## Caso vulnerable

Archivo: `samples/vulnerable.sol`

Resultado esperado y verificado:

- 7 hallazgos totales.
- 1 hallazgo de severidad alta.
- 5 hallazgos de severidad media.
- 1 hallazgo de severidad baja.

Reglas detectadas en el caso de demostración:

- SG001 — versión antigua de Solidity.
- SG002 — uso de `tx.origin`.
- SG003 — uso de `selfdestruct`.
- SG004 — posible patrón de reentrancy.
- SG005 — llamada de bajo nivel sin verificar.
- SG006 — uso de `delegatecall`.
- SG008 — aleatoriedad basada en variables de bloque.

## Caso más seguro

Archivo: `samples/safer.sol`

Resultado esperado y verificado:

- 0 hallazgos para las reglas actualmente configuradas.

Este resultado **no significa que el contrato sea seguro**. Solo indica que no coincide con las heurísticas implementadas en la versión 0.2.

## Pruebas automáticas

La suite contiene 12 pruebas unitarias que verifican detecciones positivas, casos negativos y que los comentarios no activen reglas por error.
