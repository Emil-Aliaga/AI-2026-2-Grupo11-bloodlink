# BLOODLINK + IA | Equipo 11

**Demo pública:** https://ai-2026-2-grupo11-bloodlinkia-dzlswkgqeeww5bzyaiaj7x.streamlit.app/

## Problema real
En el Perú, bancos de sangre y hospitales deben coordinar un recurso limitado y perecible para atender emergencias, cirugías, tratamientos oncológicos y otras necesidades transfusionales. El Minsa informó que en 2024 se recolectaron **481 232 unidades de sangre** y que solo **20 %** provinieron de donación voluntaria. BLOODLINK IA simula la distribución de stock limitado entre hospitales con solicitudes de distinta prioridad y plazo.

El problema lo enfrentan los **equipos de bancos de sangre, servicios de hemoterapia y responsables logísticos hospitalarios**. Las prioridades **P1/P2/P3** son datos sintéticos ya asignados por el hospital; BLOODLINK no realiza diagnóstico ni triage clínico.

## Parte 1
- **FIFO (modo base):** atiende por orden de llegada.
- **Agente basado en objetivos:** prioriza P1 y luego el plazo más próximo.
- **Agente basado en utilidad:** evalúa prioridad, urgencia, vencimiento, distancia e impacto sobre stock.

Las tres estrategias reciben el mismo escenario, usan stock por **FEFO** y no utilizan lotes vencidos.

**Métrica principal:** % de solicitudes P1 atendidas dentro del plazo.  
**Métricas secundarias:** solicitudes atendidas, tiempo medio de entrega, desperdicio, distancia y tiempo de cómputo.

| Técnica | P1 a tiempo | Atendidas | Desperdicio | CPU prom. | Corridas |
|---|---:|---:|---:|---:|---:|
| FIFO (base) | 31.49% | 78.56% | 23.63 u. | 0.44 ms | 30 |
| Objetivos | **71.59%** | 78.22% | 23.67 u. | 0.42 ms | 30 |
| Utilidad | 68.67% | **80.33%** | **18.77 u.** | 1.70 ms | 30 |

Resultados de referencia: semillas 2026–2055, 30 solicitudes por escenario y 30 % de P1.

## Ejecución, IA y roles
**Local:** `pip install -r requirements.txt` → `streamlit run app.py`  
**Tecnología:** Python + Streamlit + pandas + matplotlib.

**IA generativa:** se utilizó como apoyo para estructurar código, documentación y pruebas. El equipo revisó y modificó la simulación, FEFO, control de vencimiento, agentes, métricas y comparación experimental.

**Roles:** Jhonn Eusebio — simulación y stock/FEFO · Emil Aliaga — Métricas y agentes · Gianpiere Maqui — agentes y experimentación.

**Fuentes:** [Minsa — donación de sangre en el Perú](https://www.gob.pe/institucion/minsa/noticias/1156362-tu-gesto-puede-hacer-la-diferencia-solo-el-1-36-de-la-poblacion-en-el-peru-ha-donado-sangre) · [Minsa — campaña para hospitales de Lima y Callao](https://www.gob.pe/institucion/minsa/noticias/1346703-minsa-recauda-218-unidades-de-sangre-para-654-pacientes-en-campana-conjunta-con-la-atu).
