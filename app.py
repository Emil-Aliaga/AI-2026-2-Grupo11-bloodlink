from __future__ import annotations

import matplotlib.pyplot as plt
import streamlit as st

from experiments import compare_one_scenario, run_experiment
from simulation import generate_scenario, request_table, scenario_stock_table

st.set_page_config(page_title="BLOODLINK IA", page_icon="🩸", layout="wide")

st.title("🩸 BLOODLINK IA")
st.caption("Avance Parte 1 · FIFO vs. agente de objetivos vs. agente de utilidad")
st.info(
    "Simulador académico de logística. Las prioridades P1/P2/P3 son datos de entrada ya asignados por los hospitales; "
    "el sistema no realiza diagnóstico, triage ni decisiones clínicas."
)

st.markdown(
    """
**Problema real.** En escenarios de alta demanda, responsables logísticos deben distribuir un stock limitado de unidades de sangre entre hospitales con solicitudes de distinta prioridad, plazo y distancia.

**Comparación del hito.** FIFO (modo base) → agente basado en objetivos → agente basado en utilidad. Los tres reciben exactamente el mismo escenario y se comparan con la misma métrica principal.
    """
)

with st.sidebar:
    st.header("Escenario")
    seed = st.number_input("Semilla", min_value=1, max_value=999999, value=2026, step=1)
    n_requests = st.slider("Solicitudes", 12, 60, 30, 1)
    p1_ratio = st.slider("Proporción P1", 0.10, 0.70, 0.30, 0.05)

    st.header("Agente de utilidad")
    w_priority = st.slider("Peso prioridad", 0.0, 1.0, 0.45, 0.05)
    w_urgency = st.slider("Peso urgencia", 0.0, 1.0, 0.25, 0.05)
    w_expiry = st.slider("Peso vencimiento", 0.0, 1.0, 0.15, 0.05)
    w_transport = st.slider("Peso distancia", 0.0, 1.0, 0.10, 0.05)
    w_stock = st.slider("Peso impacto en stock", 0.0, 1.0, 0.05, 0.05)
    weights = {
        "priority": w_priority,
        "urgency": w_urgency,
        "expiry": w_expiry,
        "transport": w_transport,
        "stock": w_stock,
    }
    st.caption(f"Suma de pesos: {sum(weights.values()):.2f} (son pesos relativos; no es obligatorio que sumen 1).")

scenario = generate_scenario(seed=int(seed), n_requests=n_requests, p1_ratio=p1_ratio)
comparison, details = compare_one_scenario(scenario, weights)


def draw_map():
    fig, ax = plt.subplots(figsize=(7, 5))
    for bank in scenario.banks:
        ax.scatter(bank.x, bank.y, marker="s", s=140, label=None)
        ax.text(bank.x + 0.25, bank.y + 0.25, bank.bank_id, fontsize=9)
    for hospital in scenario.hospitals:
        ax.scatter(hospital.x, hospital.y, marker="o", s=100, label=None)
        ax.text(hospital.x + 0.25, hospital.y + 0.25, hospital.hospital_id, fontsize=9)
    ax.set_xlim(0, 20)
    ax.set_ylim(0, 20)
    ax.set_xlabel("X (km simulados)")
    ax.set_ylabel("Y (km simulados)")
    ax.set_title("Red logística simulada")
    ax.grid(alpha=0.2)
    return fig


# Resumen del hito: exactamente lo que pide la guía.
st.subheader("Resumen del avance")
col1, col2, col3 = st.columns(3)
col1.metric("Modo base", "FIFO")
col2.metric("Técnica 1", "Objetivos")
col3.metric("Técnica 2", "Utilidad")
st.caption("Métrica principal: porcentaje de solicitudes P1 atendidas dentro del plazo.")

tab1, tab2, tab3, tab4 = st.tabs(
    ["1 · Escenario", "2 · Comparar", "3 · 30 corridas", "4 · Sustentación"]
)

with tab1:
    c1, c2 = st.columns([1, 1])
    with c1:
        st.pyplot(draw_map(), clear_figure=True)
    with c2:
        st.subheader("Stock inicial")
        st.dataframe(scenario_stock_table(scenario), use_container_width=True, height=300)
    st.subheader("Solicitudes del escenario")
    st.dataframe(request_table(scenario), use_container_width=True, height=360, hide_index=True)

with tab2:
    st.subheader("Modo base + dos técnicas del Bloque 1")
    show = comparison.rename(
        columns={
            "p1_on_time_rate": "P1 a tiempo (%)",
            "served_rate": "Atendidas (%)",
            "avg_delivery_h": "Entrega prom. (h)",
            "wasted_units": "Desperdicio (u.)",
            "total_distance_km": "Distancia (km)",
            "cpu_ms": "CPU (ms)",
        }
    )
    st.dataframe(show, use_container_width=True, hide_index=True)

    winner_idx = comparison["p1_on_time_rate"].idxmax()
    winner = comparison.loc[winner_idx, "Técnica"]
    winner_value = comparison.loc[winner_idx, "p1_on_time_rate"]
    st.success(
        f"En este escenario, {winner} obtiene la mejor métrica principal: {winner_value:.2f}% de P1 atendidas dentro del plazo."
    )

    strategy = st.selectbox(
        "Ver trazabilidad de decisiones",
        ["fifo", "goal", "utility"],
        format_func=lambda x: {
            "fifo": "FIFO (base)",
            "goal": "Agente de objetivos",
            "utility": "Agente de utilidad",
        }[x],
    )
    detail = details[strategy].rename(
        columns={
            "request_id": "Solicitud",
            "hospital_id": "Hospital",
            "blood_type": "Tipo",
            "units": "Unidades",
            "priority": "Prioridad",
            "status": "Estado",
            "bank_id": "Banco",
            "dispatch_time_h": "Despacho_h",
            "arrival_time_h": "Llegada_h",
            "due_time_h": "Límite_h",
            "distance_km": "Dist_km",
            "on_time": "A_tiempo",
            "utility": "Utilidad",
            "decision_reason": "Razón",
        }
    )
    preferred_cols = [
        "Solicitud", "Hospital", "Tipo", "Unidades", "Prioridad", "Estado", "Banco",
        "Despacho_h", "Llegada_h", "Límite_h", "A_tiempo", "Dist_km", "Utilidad", "Razón"
    ]
    st.dataframe(detail[[c for c in preferred_cols if c in detail.columns]], use_container_width=True, height=390, hide_index=True)

with tab3:
    st.subheader("Experimento reproducible")
    st.write(
        "Cada estrategia recibe exactamente los mismos escenarios. Se reportan promedios para evitar concluir a partir de una sola corrida."
    )
    runs = st.slider("Número de corridas", 5, 50, 30, 5, key="runs")
    if st.button("Ejecutar experimento", type="primary"):
        with st.spinner("Ejecutando FIFO, Objetivos y Utilidad sobre los mismos escenarios..."):
            summary, raw = run_experiment(
                n_runs=runs,
                base_seed=int(seed),
                n_requests=n_requests,
                p1_ratio=p1_ratio,
                weights=weights,
            )
        show_summary = summary.rename(
            columns={
                "p1_on_time_rate": "P1 a tiempo (%)",
                "served_rate": "Atendidas (%)",
                "avg_delivery_h": "Entrega prom. (h)",
                "wasted_units": "Desperdicio prom.",
                "total_distance_km": "Distancia prom. (km)",
                "cpu_ms": "CPU prom. (ms)",
            }
        )
        st.dataframe(show_summary, use_container_width=True, hide_index=True)
        st.bar_chart(show_summary.set_index("Técnica")[["P1 a tiempo (%)", "Atendidas (%)"]])
        best_main = show_summary.loc[show_summary["P1 a tiempo (%)"].idxmax()]
        best_waste = show_summary.loc[show_summary["Desperdicio prom."].idxmin()]
        st.write(
            f"**Lectura:** {best_main['Técnica']} lidera P1 a tiempo ({best_main['P1 a tiempo (%)']:.2f}%). "
            f"{best_waste['Técnica']} presenta el menor desperdicio promedio ({best_waste['Desperdicio prom.']:.2f} u.)."
        )
        st.download_button(
            "Descargar resultados CSV",
            raw.to_csv(index=False).encode("utf-8"),
            "bloodlink_experimento.csv",
            "text/csv",
        )
    else:
        st.caption("Presiona «Ejecutar experimento» para obtener la tabla de varias corridas con los parámetros actuales.")

with tab4:
    st.markdown(
        """
### Qué representa cada estrategia
- **FIFO (base):** atiende primero la solicitud que llegó primero; no usa prioridad.
- **Agente basado en objetivos:** persigue una meta explícita: priorizar P1 y, dentro de la misma prioridad, el plazo más próximo.
- **Agente basado en utilidad:** puntúa cada asignación factible usando prioridad, urgencia, cercanía al vencimiento, distancia e impacto sobre el stock.

### Reglas comunes para una comparación justa
- Los tres agentes ven únicamente solicitudes que ya llegaron.
- FIFO y Objetivos usan el banco factible más cercano.
- Los lotes se consumen mediante **FEFO** (primero vence, primero sale).
- No se permite usar un lote ya vencido.
- La compatibilidad sanguínea está simplificada a **tipo exacto** en esta Parte 1.

### Qué debe poder explicar el equipo
1. Dónde está la política FIFO, la de objetivos y la función de utilidad.
2. Por qué todos reciben el mismo escenario y la misma semilla.
3. Por qué una técnica gana la métrica principal en sus corridas.
4. Qué esperan que ocurra si cambia la proporción P1 o los pesos de utilidad.
5. Qué limitaciones impiden usar este prototipo para decisiones clínicas reales.
        """
    )
