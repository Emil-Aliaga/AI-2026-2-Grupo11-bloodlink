import copy

from agents import DEFAULT_WEIGHTS
from experiments import run_experiment
from simulation import generate_scenario, simulate_strategy


def main():
    s1 = generate_scenario(seed=2026)
    s2 = generate_scenario(seed=2026)
    assert [(r.request_id, r.priority, r.request_time_h) for r in s1.requests] == [
        (r.request_id, r.priority, r.request_time_h) for r in s2.requests
    ]

    for strategy in ["fifo", "goal", "utility"]:
        metrics, detail = simulate_strategy(s1, strategy, DEFAULT_WEIGHTS)
        assert 0.0 <= metrics["p1_on_time_rate"] <= 100.0
        assert metrics["served_requests"] + metrics["unserved_requests"] == len(s1.requests)
        if not detail.empty:
            served = detail[detail["status"] == "ATENDIDA"]
            assert (served["arrival_time_h"] >= served["dispatch_time_h"]).all()

    summary, raw = run_experiment(n_runs=5, base_seed=2026)
    assert len(summary) == 3
    assert len(raw) == 15
    print("OK: pruebas de humo completadas")
    print(summary.to_string(index=False))


if __name__ == "__main__":
    main()
