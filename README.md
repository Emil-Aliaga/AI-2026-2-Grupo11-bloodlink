# BLOODLINK IA | Equipo 11

**Demo pública:** https://ai-2026-2-grupo11-bloodlinkia-dzlswkgqeeww5bzyaiaj7x.streamlit.app/

## Problema real
En el Perú, bancos de sangre y hospitales deben coordinar un recurso limitado y perecible para atender emergencias, cirugías, tratamientos oncológicos y otras necesidades transfusionales. El Minsa informó que en 2024 se recolectaron **481 232 unidades de sangre** y que solo **20 %** provinieron de donación voluntaria. BLOODLINK IA convierte ese reto en un **simulador académico de logística**: varios hospitales envían solicitudes con prioridad, plazo y tipo sanguíneo, mientras varios bancos disponen de stock limitado con vencimiento.

Quienes sufren el problema son los **equipos de bancos de sangre, servicios de hemoterapia y responsables logísticos hospitalarios**, que deben decidir qué atender primero y desde dónde despachar. Los pacientes son los afectados indirectos cuando una atención no llega oportunamente. Las prioridades **P1/P2/P3** son datos sintéticos ya asignados por el hospital; BLOODLINK **no realiza diagnóstico ni triage clínico**.

## Parte 1: tres formas de resolver el mismo problema
- **FIFO (modo base):** atiende la primera solicitud disponible por orden de llegada.
- **Agente basado en objetivos:** busca atender primero las solicitudes P1 y, dentro de la prioridad, las de plazo más cercano.
- **Agente basado en utilidad:** evalúa alternativas mediante `U = prioridad + urgencia + vencimiento − distancia − impacto_stock` y selecciona la mayor utilidad.

Las tres estrategias reciben **exactamente el mismo escenario**, usan stock por **FEFO** (primero vence, primero sale) y no utilizan lotes vencidos.

**Métrica principal común:** `% de solicitudes P1 atendidas dentro del plazo`.  
Métricas secundarias: solicitudes atendidas, tiempo medio de entrega, desperdicio, distancia y tiempo de cómputo.

| Técnica | P1 a tiempo | Atendidas | Desperdicio | CPU prom. | Corridas |
|---|---:|---:|---:|---:|---:|
| FIFO (base) | 31.49% | 78.56% | 23.63 u. | 0.44 ms | 30 |
| Objetivos | **71.59%** | 78.22% | 23.67 u. | 0.42 ms | 30 |
| Utilidad | 68.67% | **80.33%** | **18.77 u.** | 1.70 ms | 30 |

Resultados de referencia: semillas 2026–2055, 30 solicitudes por escenario y 30 % de P1.

## Giro innovador del avance
Además de la tabla comparativa, BLOODLINK muestra **trazabilidad de decisiones**: permite observar qué solicitud eligió cada estrategia, el banco asignado, el tiempo límite y si llegó a tiempo. Para el agente de utilidad se visualiza la contribución de **prioridad, urgencia, vencimiento, distancia y stock**, haciendo explicable la decisión. Los parámetros pueden modificarse en vivo para realizar una **prueba de estrés** y comprobar cómo cambia el resultado.

## Ejecución, IA y roles
**Local:** `pip install -r requirements.txt` → `streamlit run app.py`.  
**Tecnología:** Python + Streamlit + pandas + matplotlib; datos 100 % sintéticos.

**IA generativa:** se utilizó para apoyar la estructura inicial de código, documentación y pruebas. El equipo revisó y modificó la lógica de simulación, FEFO, control de vencimiento, agentes, métricas, trazabilidad y comparación experimental.

**Roles:** Integrante 1 — lógica de simulación y stock/FEFO · Integrante 2 — agentes y experimentación · Integrante 3 — interfaz, visualización y despliegue. Los tres revisan resultados y deben poder explicar el código.

**Fuentes de contexto peruano:** [Minsa — donación de sangre en el Perú](https://www.gob.pe/institucion/minsa/noticias/1156362-tu-gesto-puede-hacer-la-diferencia-solo-el-1-36-de-la-poblacion-en-el-peru-ha-donado-sangre) · [Minsa — campaña para hospitales de Lima y Callao](https://www.gob.pe/institucion/minsa/noticias/1346703-minsa-recauda-218-unidades-de-sangre-para-654-pacientes-en-campana-conjunta-con-la-atu).
