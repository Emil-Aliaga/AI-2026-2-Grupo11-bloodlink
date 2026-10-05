# BLOODLINK IA — Equipo ##

**Problema y quién lo sufre.** BLOODLINK IA es un simulador académico de distribución logística de unidades de sangre entre bancos y hospitales en escenarios de alta demanda. El problema lo enfrentan responsables logísticos cuando el stock es limitado y existen solicitudes con distinta prioridad, distancia y plazo. Las prioridades P1/P2/P3 ya vienen asignadas por los hospitales; el sistema no realiza diagnóstico ni triage.

**Modo base y técnicas comparadas — Parte 1.** **FIFO (base)** → **agente basado en objetivos** → **agente basado en utilidad**. FIFO atiende por orden de llegada. Objetivos prioriza P1 y luego el plazo más próximo. Utilidad pondera prioridad, urgencia, cercanía al vencimiento, distancia e impacto sobre el stock. Los tres reciben el mismo escenario, las mismas solicitudes y consumen lotes mediante FEFO; no se usan lotes vencidos.

**Métrica común.** Métrica principal: **% de solicitudes P1 atendidas dentro del plazo**. Secundarias: cobertura total, tiempo medio de entrega, desperdicio, distancia y tiempo de cómputo.

| Técnica | P1 a tiempo | Atendidas | Desperdicio | CPU prom. | Corridas |
|---|---:|---:|---:|---:|---:|
| FIFO (base) | 31.49% | 78.56% | 23.63 u. | 0.44 ms | 30 |
| Objetivos | **71.59%** | 78.22% | 23.67 u. | 0.42 ms | 30 |
| Utilidad | 68.67% | **80.33%** | **18.77 u.** | 1.70 ms | 30 |

Resultados de referencia: semillas 2026–2055, 30 solicitudes por escenario, 30% P1 y pesos de utilidad 0.45/0.25/0.15/0.10/0.05. La app permite repetir las corridas y cambiar parámetros en vivo.

**Cómo ejecutarlo.** Local: `pip install -r requirements.txt` y luego `streamlit run app.py`. En Streamlit Community Cloud: crear el repositorio `AI-2026-2-Equipo##-bloodlink`, subir estos archivos, conectar la rama `main` y seleccionar `app.py` como archivo principal.

**Uso de IA generativa.** Se utilizó IA generativa como apoyo para estructurar la primera versión del código, documentación y pruebas. El equipo revisó y modificó la lógica de simulación, control de vencimiento, FEFO, trazabilidad, métricas y comparación experimental. Cada integrante debe poder ubicar y explicar el código presentado.

**Roles.** Integrante 1 — completar rol y commits · Integrante 2 — completar · Integrante 3 — completar · Integrante 4 — completar.

**Lenguaje y alcance.** Python + Streamlit + pandas + matplotlib. Datos sintéticos, compatibilidad exacta por tipo sanguíneo y un canal de despacho. Prototipo educativo de logística; no sustituye protocolos clínicos ni sistemas hospitalarios reales.
