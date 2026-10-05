
# BLOODLINK IA — Equipo 11

 En el Perú, mantener un abastecimiento oportuno de sangre es una necesidad permanente para atender emergencias, cirugías de alta complejidad, tratamientos oncológicos y complicaciones obstétricas. El Minsa informó que en 2024 se recolectaron **481 232 unidades de sangre** y que solo **20 %** provinieron de donantes voluntarios, mientras que **80 %** correspondieron a reposición. Además, en febrero de 2026 una campaña del Minsa reunió **218 unidades** destinadas a beneficiar pacientes de **siete hospitales de Lima Metropolitana y Callao**, mostrando que la disponibilidad y distribución entre distintos establecimientos es un problema real de coordinación. En este contexto, BLOODLINK IA simula el reto logístico de asignar un stock limitado entre hospitales con solicitudes de distinta prioridad y plazo. El problema lo enfrentan principalmente los equipos de bancos de sangre, servicios de hemoterapia y responsables logísticos hospitalarios; indirectamente afecta a los pacientes que necesitan una transfusión oportuna. Las prioridades P1/P2/P3 del prototipo son datos simulados ya asignados por el hospital: BLOODLINK no realiza diagnóstico, triage ni decisiones clínicas.

**Modo base y técnicas comparadas — Parte 1.** **FIFO (base)** → **agente basado en objetivos** → **agente basado en utilidad**. FIFO atiende por orden de llegada. Objetivos prioriza P1 y luego el plazo más próximo. Utilidad pondera prioridad, urgencia, cercanía al vencimiento, distancia e impacto sobre el stock. Los tres reciben exactamente el mismo escenario y las mismas solicitudes; los lotes se consumen mediante FEFO y nunca se utilizan unidades vencidas.

**Métrica común.** Métrica principal: **% de solicitudes P1 atendidas dentro del plazo**. Como métricas secundarias se muestran cobertura total, tiempo medio de entrega, desperdicio, distancia y tiempo de cómputo.

| Técnica | P1 a tiempo | Atendidas | Desperdicio | CPU prom. | Corridas |
|---|---:|---:|---:|---:|---:|
| FIFO (base) | 31.49% | 78.56% | 23.63 u. | 0.44 ms | 30 |
| Objetivos | **71.59%** | 78.22% | 23.67 u. | 0.42 ms | 30 |
| Utilidad | 68.67% | **80.33%** | **18.77 u.** | 1.70 ms | 30 |

Resultados de referencia: semillas 2026–2055, 30 solicitudes por escenario, 30 % P1 y pesos de utilidad 0.45/0.25/0.15/0.10/0.05. La aplicación permite repetir las corridas y modificar parámetros en vivo.

**Uso de IA generativa.** Se utilizó IA generativa como apoyo para estructurar una primera versión del código, documentación y pruebas. El equipo revisó, modificó y validó la lógica de simulación, control de vencimiento, FEFO, trazabilidad, métricas y comparación experimental. Cada integrante debe poder ubicar y explicar el código presentado.

**Roles.** Integrante 1 — Lógica de simulación · Integrante 2 — Agentes y experimentación · Integrante 3 — Interfaz y despliegue.

**Lenguaje y alcance.** Python + Streamlit + pandas + matplotlib. El prototipo utiliza **datos sintéticos** y compatibilidad exacta por tipo sanguíneo para comparar estrategias de decisión. Es una simulación académica de logística y **no representa un protocolo clínico ni sustituye sistemas hospitalarios reales**.

Demo pública: https://ai-2026-2-grupo11-bloodlinkia-dzlswkgqeeww5bzyaiaj7x.streamlit.app/

Ministerio de Salud del Perú: [Donación de sangre en el Perú](https://www.gob.pe/institucion/minsa/noticias/1156362-tu-gesto-puede-hacer-la-diferencia-solo-el-1-36-de-la-poblacion-en-el-peru-ha-donado-sangre) · [Campaña Minsa–ATU para siete hospitales de Lima y Callao](https://www.gob.pe/institucion/minsa/noticias/1346703-minsa-recauda-218-unidades-de-sangre-para-654-pacientes-en-campana-conjunta-con-la-atu) · [Bancos de sangre autorizados](https://www.gob.pe/institucion/minsa/informes-publicaciones/4483387).
