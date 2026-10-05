from __future__ import annotations

from typing import Dict, List, Optional

import pandas as pd

from agents import DEFAULT_WEIGHTS
from simulation import generate_scenario, simulate_strategy


STRATEGY_LABEL = {
    "fifo": "FIFO (base)",
    "goal": "Agente de objetivos",
    "utility": "Agente de utilidad",
}


def compare_one_scenario(scenario, weights: Optional[Dict[str, float]] = None):
    rows = []
    details = {}
    for strategy in ["fifo", "goal", "utility"]:
        metrics, df = simulate_strategy(scenario, strategy, weights or DEFAULT_WEIGHTS)
        metrics["Técnica"] = STRATEGY_LABEL[strategy]
        rows.append(metrics)
        details[strategy] = df
    result = pd.DataFrame(rows)
    cols = [
        "Técnica",
        "p1_on_time_rate",
        "served_rate",
        "avg_delivery_h",
        "wasted_units",
        "total_distance_km",
        "cpu_ms",
    ]
    return result[cols], details


def run_experiment(
    n_runs: int = 30,
    base_seed: int = 2026,
    n_requests: int = 30,
    p1_ratio: float = 0.30,
    weights: Optional[Dict[str, float]] = None,
):
    rows: List[dict] = []
    for i in range(n_runs):
        scenario = generate_scenario(
            seed=base_seed + i,
            n_requests=n_requests,
            p1_ratio=p1_ratio,
        )
        for strategy in ["fifo", "goal", "utility"]:
            metrics, _ = simulate_strategy(scenario, strategy, weights or DEFAULT_WEIGHTS)
            metrics["run"] = i + 1
            metrics["seed"] = base_seed + i
            metrics["strategy_label"] = STRATEGY_LABEL[strategy]
            rows.append(metrics)

    raw = pd.DataFrame(rows)
    summary = (
        raw.groupby(["strategy", "strategy_label"], as_index=False)
        .agg(
            p1_on_time_rate=("p1_on_time_rate", "mean"),
            served_rate=("served_rate", "mean"),
            avg_delivery_h=("avg_delivery_h", "mean"),
            wasted_units=("wasted_units", "mean"),
            total_distance_km=("total_distance_km", "mean"),
            cpu_ms=("cpu_ms", "mean"),
        )
    )
    for c in ["p1_on_time_rate", "served_rate", "avg_delivery_h", "wasted_units", "total_distance_km", "cpu_ms"]:
        summary[c] = summary[c].round(2)
    summary = summary.rename(columns={"strategy_label": "Técnica"})
    return summary, raw
