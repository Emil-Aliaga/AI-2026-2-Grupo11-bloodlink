from __future__ import annotations

import matplotlib.pyplot as plt
import pandas as pd
import streamlit as st

from experiments import compare_one_scenario, run_experiment
from simulation import generate_scenario, request_table, scenario_stock_table

st.set_page_config(page_title="Bloodlink + IA", page_icon="🩸", layout="wide")

st.title("🩸 Bloodlink + IA")
st.caption("Avance 1 · Simulador de distribución logística de sangre")

st.markdown(
    """
**Problema:** distribuir stock limitado de sangre entre hospitales con solicitudes de distinta prioridad,
plazo, distancia y vencimiento.

**Comparación:** **FIFO (base)** → **Agente de objetivos** → **Agente de utilidad**.
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

scenario = generate_scenario(
    seed=int(seed),
    n_requests=n_requests,
    p1_ratio=p1_ratio,
)
comparison, details = compare_one_scenario(scenario, weights)


def draw_map():
    fig, ax = plt.subplots(figsize=(7, 5))
    for bank in scenario.banks:
        ax.scatter(bank.x, bank.y, marker="s", s=140)
        ax.text(bank.x + 0.25, bank.y + 0.25, bank.bank_id, fontsize=9)
    for hospital in scenario.hospitals:
        ax.scatter(hospital.x, hospital.y, marker="o", s=100)
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


col1, col2, col3 = st.columns(3)
col1.metric("Modo base", "FIFO")
col2.metric("Técnica 1", "Objetivos")
col3.metric("Técnica 2", "Utilidad")
st.caption("Métrica principal: % de solicitudes P1 atendidas dentro del plazo.")

tab1, tab2, tab3 = st.tabs(
    ["1 · Escenario", "2 · Comparar", "3 · Experimento"]
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
    with c2:
        st.subheader("Stock inicial")
        st.dataframe(
            scenario_stock_table(scenario),
            use_container_width=True,
            height=300,
            hide_index=True,
        )

    st.subheader("Solicitudes")
    st.dataframe(
        request_table(scenario),
        use_container_width=True,
        height=360,
        hide_index=True,
    )

with tab2:
    st.subheader("Resultados del escenario")

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
        delta = None if technique == "FIFO (base)" else f"{value - fifo_value:+.2f} pp"
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
    st.success(f"{winner}: {winner_value:.2f}% de P1 atendidas dentro del plazo.")

    st.divider()
    st.subheader("Caso P1")

    fifo_df = details["fifo"]
    goal_df = details["goal"]
    utility_df = details["utility"]

    critical_ids = []
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
        critical_id = st.selectbox("Solicitud P1", critical_ids)
        critical_table = pd.DataFrame(
            [
                outcome_for_request(fifo_df, critical_id, "FIFO (base)"),
                outcome_for_request(goal_df, critical_id, "Objetivos"),
                outcome_for_request(utility_df, critical_id, "Utilidad"),
            ]
        )
        st.dataframe(critical_table, use_container_width=True, hide_index=True)
    else:
        st.write("No hay un caso P1 diferencial con los parámetros actuales.")

    st.divider()
    st.subheader("Trazabilidad")

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
            st.subheader("Descomposición de utilidad")
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
                f"**Banco:** {r.get('bank_id', '—')}"
            )

with tab3:
    st.subheader("Comparación con varias simulaciones")
    runs = st.slider("Cantidad de simulaciones", 5, 50, 30, 5, key="runs")

    if st.button("Ejecutar experimento", type="primary"):
        with st.spinner("Ejecutando..."):
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
            show_summary.set_index("Técnica")[["P1 a tiempo (%)", "Atendidas (%)"]]
        )

        best_main = show_summary.loc[show_summary["P1 a tiempo (%)"].idxmax()]
        best_waste = show_summary.loc[show_summary["Desperdicio prom."].idxmin()]

        st.success(
            f"{best_main['Técnica']}: {best_main['P1 a tiempo (%)']:.2f}% de P1 a tiempo."
        )
        st.write(
            f"Menor desperdicio: **{best_waste['Técnica']}** "
            f"({best_waste['Desperdicio prom.']:.2f} u.)."
        )

        st.download_button(
            "Descargar resultados CSV",
            raw.to_csv(index=False).encode("utf-8"),
            "bloodlink_experimento.csv",
            "text/csv",
        )
