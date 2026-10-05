from __future__ import annotations

import matplotlib.pyplot as plt
import pandas as pd
import streamlit as st

from experiments import compare_one_scenario, run_experiment
from simulation import generate_scenario, request_table, scenario_stock_table

st.set_page_config(page_title="BLOODLINK IA", page_icon="🩸", layout="wide")

st.title("🩸 BLOODLINK IA")
st.caption("Avance 1 · Simulador inteligente de distribución logística de sangre")

st.info(
    "Prototipo académico con datos sintéticos inspirado en la coordinación logística entre bancos de sangre "
    "y hospitales del Perú. Las prioridades P1/P2/P3 ya vienen asignadas por el hospital; BLOODLINK no realiza "
    "diagnóstico, triage ni decisiones clínicas."
)

st.markdown(
    """
**Problema.** Cuando el stock es limitado, un responsable logístico debe decidir qué solicitud atender primero
y desde qué banco despacharla, considerando prioridad, plazo, distancia y vencimiento del inventario.

**Tres formas de resolverlo:** **FIFO (base)** → **agente basado en objetivos** → **agente basado en utilidad**.
Las tres reciben exactamente el mismo escenario y se comparan con la misma métrica principal.
"""
)

flow1, flow2, flow3 = st.columns(3)
flow1.markdown("**👁️ Percibe**  \nSolicitudes · stock · hora · vencimientos")
flow2.markdown("**🧠 Decide**  \nFIFO · objetivo · utilidad")
flow3.markdown("**🚚 Actúa**  \nAsigna stock · despacha · registra resultado")

with st.sidebar:
    st.header("Escenario")
    seed = st.number_input(
        "Semilla",
        min_value=1,
        max_value=999999,
        value=2026,
        step=1,
        help="Permite reproducir exactamente el mismo escenario."
    )
    n_requests = st.slider(
        "Solicitudes",
        12,
        60,
        30,
        1,
        help="Aumenta la presión sobre el inventario y el canal de despacho."
    )
    p1_ratio = st.slider(
        "Proporción P1",
        0.10,
        0.70,
        0.30,
        0.05,
        help="P1 = prioridad alta, P2 = media y P3 = baja. La prioridad ya viene asignada por el hospital."
    )
    st.caption("💡 Prueba de estrés: aumenta P1 o el número de solicitudes y vuelve a comparar.")

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
    st.caption(
        f"Suma de pesos: {sum(weights.values()):.2f}. Son pesos relativos y pueden modificarse en vivo."
    )

scenario = generate_scenario(
    seed=int(seed),
    n_requests=n_requests,
    p1_ratio=p1_ratio,
)
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


def outcome_for_request(df: pd.DataFrame, request_id: str, label: str) -> dict:
    row = df[df["request_id"] == request_id]
    if row.empty:
        return {
            "Estrategia": label,
            "Estado": "—",
            "Llegada (h)": "—",
            "Límite (h)": "—",
            "A tiempo": "—",
        }
    r = row.iloc[0]
    arrival = "—" if pd.isna(r.get("arrival_time_h")) else f"{float(r['arrival_time_h']):.2f}"
    due = "—" if pd.isna(r.get("due_time_h")) else f"{float(r['due_time_h']):.2f}"
    return {
        "Estrategia": label,
        "Estado": r.get("status", "—"),
        "Llegada (h)": arrival,
        "Límite (h)": due,
        "A tiempo": "Sí" if bool(r.get("on_time", False)) else "No",
    }


st.subheader("Comparación del avance 1")
col1, col2, col3 = st.columns(3)
col1.metric("Modo base", "FIFO")
col2.metric("Técnica 1", "Agente de objetivos")
col3.metric("Técnica 2", "Agente de utilidad")
st.caption(
    "Métrica principal común: % de solicitudes P1 atendidas dentro del plazo. "
    "P1 = prioridad alta, P2 = media, P3 = baja."
)

tab1, tab2, tab3 = st.tabs(
    ["1 · Escenario", "2 · Decisiones y comparación", "3 · Experimento"]
)

with tab1:
    m1, m2, m3, m4 = st.columns(4)
    m1.metric("Bancos", len(scenario.banks))
    m2.metric("Hospitales", len(scenario.hospitals))
    m3.metric("Solicitudes", len(scenario.requests))
    p1_count = sum(1 for r in scenario.requests if r.priority == "P1")
    m4.metric("Solicitudes P1", p1_count)

    c1, c2 = st.columns([1, 1])
    with c1:
        st.pyplot(draw_map(), clear_figure=True)
        st.caption("Mapa esquemático: las coordenadas son simuladas y se usan para calcular distancia y tiempo.")
    with c2:
        st.subheader("Stock inicial")
        st.dataframe(
            scenario_stock_table(scenario),
            use_container_width=True,
            height=300,
            hide_index=True,
        )

    st.subheader("Solicitudes del escenario")
    st.dataframe(
        request_table(scenario),
        use_container_width=True,
        height=360,
        hide_index=True,
    )

with tab2:
    st.subheader("¿Cuál estrategia atiende mejor las P1 a tiempo?")

    fifo_value = float(
        comparison.loc[comparison["Técnica"] == "FIFO (base)", "p1_on_time_rate"].iloc[0]
    )
    metric_cols = st.columns(3)
    for col, technique in zip(
        metric_cols,
        ["FIFO (base)", "Agente de objetivos", "Agente de utilidad"],
    ):
        row = comparison[comparison["Técnica"] == technique].iloc[0]
        value = float(row["p1_on_time_rate"])
        delta = None if technique == "FIFO (base)" else f"{value - fifo_value:+.2f} pp vs FIFO"
        col.metric(technique, f"{value:.2f}%", delta)

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
    winner_value = float(comparison.loc[winner_idx, "p1_on_time_rate"])
    best_waste_idx = comparison["wasted_units"].idxmin()
    best_waste = comparison.loc[best_waste_idx, "Técnica"]
    best_waste_value = float(comparison.loc[best_waste_idx, "wasted_units"])

    st.success(
        f"En este escenario, **{winner}** lidera la métrica principal con **{winner_value:.2f}%** de P1 a tiempo."
    )
    st.caption(
        f"Trade-off: **{best_waste}** presenta el menor desperdicio ({best_waste_value:.0f} unidades). "
        "Una estrategia puede ganar la métrica principal sin dominar todas las métricas secundarias."
    )

    st.divider()
    st.subheader("🔎 Caso crítico: una decisión donde la estrategia sí importa")

    critical_ids = []
    fifo_df = details["fifo"]
    goal_df = details["goal"]
    utility_df = details["utility"]

    for req in scenario.requests:
        if req.priority != "P1":
            continue
        rid = req.request_id
        f = fifo_df[fifo_df["request_id"] == rid]
        g = goal_df[goal_df["request_id"] == rid]
        u = utility_df[utility_df["request_id"] == rid]
        if f.empty or g.empty or u.empty:
            continue
        fifo_on_time = bool(f.iloc[0]["on_time"])
        goal_on_time = bool(g.iloc[0]["on_time"])
        utility_on_time = bool(u.iloc[0]["on_time"])
        if (not fifo_on_time) and (goal_on_time or utility_on_time):
            critical_ids.append(rid)

    if critical_ids:
        critical_id = st.selectbox(
            "Solicitud P1 para explicar",
            critical_ids,
            help="Se muestran casos en los que FIFO no llega a tiempo y al menos un agente inteligente sí."
        )
        critical_table = pd.DataFrame(
            [
                outcome_for_request(fifo_df, critical_id, "FIFO (base)"),
                outcome_for_request(goal_df, critical_id, "Objetivos"),
                outcome_for_request(utility_df, critical_id, "Utilidad"),
            ]
        )
        st.dataframe(critical_table, use_container_width=True, hide_index=True)
        st.info(
            "Este caso sirve para explicar con números **por qué** una técnica aporta valor frente al modo base, "
            "no solo para mostrar una tabla final."
        )
    else:
        st.caption(
            "En esta semilla no apareció un P1 donde FIFO falle y otro agente llegue a tiempo. "
            "Cambia la semilla o aumenta la proporción P1 para generar un escenario más exigente."
        )

    st.divider()
    st.subheader("Trazabilidad de decisiones")
    strategy = st.selectbox(
        "Estrategia",
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
        "Solicitud",
        "Hospital",
        "Tipo",
        "Unidades",
        "Prioridad",
        "Estado",
        "Banco",
        "Despacho_h",
        "Llegada_h",
        "Límite_h",
        "A_tiempo",
        "Dist_km",
        "Utilidad",
        "Razón",
    ]
    st.dataframe(
        detail[[c for c in preferred_cols if c in detail.columns]],
        use_container_width=True,
        height=360,
        hide_index=True,
    )

    if strategy == "utility":
        expl = details["utility"]
        explainable = expl[
            (expl["status"] == "ATENDIDA") & (expl["utility"].notna())
        ].copy()

        if not explainable.empty:
            st.subheader("🧠 ¿Por qué el agente de utilidad eligió esa opción?")
            explain_id = st.selectbox(
                "Solicitud atendida",
                explainable["request_id"].tolist(),
                key="utility_explain_request",
            )
            r = explainable[explainable["request_id"] == explain_id].iloc[0]

            e1, e2, e3, e4, e5 = st.columns(5)
            e1.metric("Prioridad +", f"{float(r.get('priority_term', 0.0)):.3f}")
            e2.metric("Urgencia +", f"{float(r.get('urgency_term', 0.0)):.3f}")
            e3.metric("Vencimiento +", f"{float(r.get('expiry_term', 0.0)):.3f}")
            e4.metric("Distancia −", f"{float(r.get('transport_penalty', 0.0)):.3f}")
            e5.metric("Stock −", f"{float(r.get('stock_penalty', 0.0)):.3f}")

            st.code(
                "U = prioridad + urgencia + vencimiento - distancia - impacto_stock",
                language="text",
            )
            st.write(
                f"**Utilidad total:** {float(r['utility']):.4f} · "
                f"**Banco elegido:** {r.get('bank_id', '—')} · "
                f"**Razón registrada:** {r.get('decision_reason', '—')}"
            )
            st.caption(
                "Los pesos pueden cambiarse en la barra lateral. Esto permite predecir y comprobar "
                "cómo cambia el comportamiento del agente durante la demostración."
            )

with tab3:
    st.subheader("Experimento con varias corridas")
    st.write(
        "Cada corrida genera un escenario diferente. Dentro de cada corrida, FIFO, Objetivos y Utilidad reciben "
        "exactamente el mismo escenario. Así evitamos comparar estrategias con condiciones distintas."
    )

    runs = st.slider(
        "Número de corridas",
        5,
        50,
        30,
        5,
        key="runs",
        help="Más corridas reducen el efecto de un escenario particularmente favorable o desfavorable."
    )

    if st.button("Ejecutar experimento", type="primary"):
        with st.spinner(
            "Ejecutando FIFO, Objetivos y Utilidad sobre los mismos escenarios..."
        ):
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
        st.bar_chart(
            show_summary.set_index("Técnica")[
                ["P1 a tiempo (%)", "Atendidas (%)"]
            ]
        )

        best_main = show_summary.loc[
            show_summary["P1 a tiempo (%)"].idxmax()
        ]
        best_waste = show_summary.loc[
            show_summary["Desperdicio prom."].idxmin()
        ]
        fifo_multi = show_summary[
            show_summary["Técnica"] == "FIFO (base)"
        ].iloc[0]

        st.success(
            f"**Resultado de {runs} corridas:** {best_main['Técnica']} lidera P1 a tiempo "
            f"con {best_main['P1 a tiempo (%)']:.2f}%."
        )
        st.write(
            f"Frente a FIFO ({fifo_multi['P1 a tiempo (%)']:.2f}%), la diferencia del ganador es "
            f"**{best_main['P1 a tiempo (%)'] - fifo_multi['P1 a tiempo (%)']:+.2f} puntos porcentuales**. "
            f"El menor desperdicio promedio corresponde a **{best_waste['Técnica']}** "
            f"({best_waste['Desperdicio prom.']:.2f} u.)."
        )

        st.download_button(
            "Descargar resultados CSV",
            raw.to_csv(index=False).encode("utf-8"),
            "bloodlink_experimento.csv",
            "text/csv",
        )
    else:
        st.caption(
            "Presiona «Ejecutar experimento» para obtener la tabla comparativa con los parámetros actuales."
        )
