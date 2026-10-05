from __future__ import annotations

import copy
import math
import random
import time
from typing import Dict, Iterable, List, Optional, Tuple

import pandas as pd

from models import BLOOD_TYPES, Batch, BloodBank, Hospital, Request, Scenario

DEFAULT_SPEED_KMH = 25.0
HANDLING_H = 0.35


def euclidean_distance(a_x: float, a_y: float, b_x: float, b_y: float) -> float:
    return math.hypot(a_x - b_x, a_y - b_y)


def generate_scenario(
    seed: int = 2026,
    n_banks: int = 3,
    n_hospitals: int = 5,
    n_requests: int = 30,
    p1_ratio: float = 0.30,
    horizon_h: float = 24.0,
) -> Scenario:
    """Genera un escenario reproducible y completamente simulado."""
    rng = random.Random(seed)

    hospitals: List[Hospital] = [
        Hospital(
            hospital_id=f"H{i+1}",
            name=f"Hospital {i+1}",
            x=round(rng.uniform(1, 19), 2),
            y=round(rng.uniform(1, 19), 2),
        )
        for i in range(n_hospitals)
    ]

    banks: List[BloodBank] = []
    batch_counter = 1
    for i in range(n_banks):
        batches: List[Batch] = []
        for blood_type in BLOOD_TYPES:
            # Stock deliberadamente limitado para que el orden de asignación importe.
            total_units = rng.randint(2, 6)
            split = rng.randint(1, total_units)
            parts = [split] + ([total_units - split] if split < total_units else [])
            for part in parts:
                batches.append(
                    Batch(
                        batch_id=f"L{batch_counter}",
                        bank_id=f"B{i+1}",
                        blood_type=blood_type,
                        units=part,
                        expires_in_h=round(rng.uniform(4, 42), 1),
                    )
                )
                batch_counter += 1

        banks.append(
            BloodBank(
                bank_id=f"B{i+1}",
                name=f"Banco {i+1}",
                x=round(rng.uniform(1, 19), 2),
                y=round(rng.uniform(1, 19), 2),
                batches=batches,
            )
        )

    p2_ratio = (1.0 - p1_ratio) * 0.58
    requests: List[Request] = []
    for i in range(n_requests):
        r = rng.random()
        if r < p1_ratio:
            priority = "P1"
            deadline = rng.uniform(0.9, 2.2)
        elif r < p1_ratio + p2_ratio:
            priority = "P2"
            deadline = rng.uniform(1.8, 4.0)
        else:
            priority = "P3"
            deadline = rng.uniform(3.0, 6.0)

        hospital = rng.choice(hospitals)
        requests.append(
            Request(
                request_id=f"R{i+1:02d}",
                hospital_id=hospital.hospital_id,
                blood_type=rng.choice(BLOOD_TYPES),
                units=rng.randint(1, 4),
                priority=priority,
                request_time_h=round(rng.uniform(0, horizon_h * 0.60), 2),
                deadline_h=round(deadline, 2),
            )
        )

    requests.sort(key=lambda x: (x.request_time_h, x.request_id))
    return Scenario(
        seed=seed,
        horizon_h=horizon_h,
        banks=banks,
        hospitals=hospitals,
        requests=requests,
        metadata={
            "n_banks": n_banks,
            "n_hospitals": n_hospitals,
            "n_requests": n_requests,
            "p1_ratio": p1_ratio,
        },
    )


def _hospital_map(scenario: Scenario) -> Dict[str, Hospital]:
    return {h.hospital_id: h for h in scenario.hospitals}


def available_units(bank: BloodBank, blood_type: str, current_time_h: float = 0.0) -> int:
    """Unidades todavía vigentes en un banco para un tipo sanguíneo."""
    return sum(
        max(0, b.units)
        for b in bank.batches
        if b.blood_type == blood_type and b.expires_in_h > current_time_h
    )


def total_available(
    banks: Iterable[BloodBank], blood_type: str, current_time_h: float = 0.0
) -> int:
    return sum(available_units(bank, blood_type, current_time_h) for bank in banks)


def expiring_score(bank: BloodBank, blood_type: str, current_time_h: float) -> float:
    """1 significa que el lote vigente más próximo a vencer está muy cerca del vencimiento."""
    lots = [
        b
        for b in bank.batches
        if b.blood_type == blood_type and b.units > 0 and b.expires_in_h > current_time_h
    ]
    if not lots:
        return 0.0
    remaining_h = min(b.expires_in_h - current_time_h for b in lots)
    return max(0.0, min(1.0, 1.0 - remaining_h / 48.0))


def transport_info(bank: BloodBank, hospital: Hospital) -> Tuple[float, float]:
    distance_km = euclidean_distance(bank.x, bank.y, hospital.x, hospital.y)
    delivery_h = HANDLING_H + distance_km / DEFAULT_SPEED_KMH
    return distance_km, delivery_h


def feasible_banks(
    scenario: Scenario, request: Request, current_time_h: float
) -> List[Tuple[BloodBank, float, float]]:
    hospital = _hospital_map(scenario)[request.hospital_id]
    options: List[Tuple[BloodBank, float, float]] = []
    for bank in scenario.banks:
        if available_units(bank, request.blood_type, current_time_h) >= request.units:
            distance, delivery_h = transport_info(bank, hospital)
            options.append((bank, distance, delivery_h))
    return options


def choose_common_bank(
    scenario: Scenario, request: Request, current_time_h: float
) -> Optional[Tuple[BloodBank, float, float]]:
    """Regla común para FIFO y objetivos: banco factible más cercano."""
    options = feasible_banks(scenario, request, current_time_h)
    if not options:
        return None
    return min(options, key=lambda t: (t[1], t[0].bank_id))


def allocate_fefo(
    bank: BloodBank, blood_type: str, units: int, current_time_h: float
) -> List[Tuple[str, int, float]]:
    """Consume lotes vigentes por FEFO (primero vence, primero sale)."""
    candidates = sorted(
        [
            b
            for b in bank.batches
            if b.blood_type == blood_type
            and b.units > 0
            and b.expires_in_h > current_time_h
        ],
        key=lambda b: (b.expires_in_h, b.batch_id),
    )
    if sum(b.units for b in candidates) < units:
        return []

    remaining = units
    used: List[Tuple[str, int, float]] = []
    for batch in candidates:
        take = min(batch.units, remaining)
        if take:
            batch.units -= take
            used.append((batch.batch_id, take, batch.expires_in_h))
            remaining -= take
        if remaining == 0:
            break
    return used


def priority_value(priority: str) -> float:
    return {"P1": 1.0, "P2": 0.62, "P3": 0.30}[priority]


def urgency_value(request: Request, current_time_h: float) -> float:
    due = request.request_time_h + request.deadline_h
    remaining = max(0.0, due - current_time_h)
    return max(0.0, min(1.0, 1.0 - remaining / 6.0))


def normalized_transport(distance_km: float) -> float:
    return max(0.0, min(1.0, distance_km / 28.0))


def stock_impact(scenario: Scenario, request: Request, current_time_h: float) -> float:
    total = total_available(scenario.banks, request.blood_type, current_time_h)
    if total <= 0:
        return 1.0
    return max(0.0, min(1.0, request.units / total))


def utility_components(
    scenario: Scenario,
    request: Request,
    bank: BloodBank,
    distance_km: float,
    weights: Dict[str, float],
    current_time_h: float,
) -> Dict[str, float]:
    p = weights["priority"] * priority_value(request.priority)
    u = weights["urgency"] * urgency_value(request, current_time_h)
    e = weights["expiry"] * expiring_score(bank, request.blood_type, current_time_h)
    t = weights["transport"] * normalized_transport(distance_km)
    s = weights["stock"] * stock_impact(scenario, request, current_time_h)
    return {
        "priority_term": p,
        "urgency_term": u,
        "expiry_term": e,
        "transport_penalty": t,
        "stock_penalty": s,
        "utility": p + u + e - t - s,
    }


def utility_score(
    scenario: Scenario,
    request: Request,
    bank: BloodBank,
    distance_km: float,
    weights: Dict[str, float],
    current_time_h: float,
) -> float:
    return utility_components(
        scenario, request, bank, distance_km, weights, current_time_h
    )["utility"]


def simulate_strategy(
    source_scenario: Scenario,
    strategy: str,
    weights: Optional[Dict[str, float]] = None,
) -> Tuple[Dict[str, float], pd.DataFrame]:
    """Simula FIFO, agente de objetivos o agente de utilidad sobre una copia del escenario."""
    scenario = copy.deepcopy(source_scenario)
    weights = weights or {
        "priority": 0.45,
        "urgency": 0.25,
        "expiry": 0.15,
        "transport": 0.10,
        "stock": 0.05,
    }

    started = time.perf_counter()
    pending = list(scenario.requests)
    deliveries: List[Dict[str, object]] = []
    current_time_h = min((r.request_time_h for r in pending), default=0.0)

    while pending:
        available = [r for r in pending if r.request_time_h <= current_time_h + 1e-9]
        if not available:
            current_time_h = min(r.request_time_h for r in pending)
            available = [r for r in pending if r.request_time_h <= current_time_h + 1e-9]

        req: Request
        option: Optional[Tuple[BloodBank, float, float]] = None
        score: Optional[float] = None
        components: Optional[Dict[str, float]] = None
        reason = ""

        if strategy == "fifo":
            req = min(available, key=lambda r: (r.request_time_h, r.request_id))
            option = choose_common_bank(scenario, req, current_time_h)
            reason = "Primera solicitud disponible por orden de llegada"
        elif strategy == "goal":
            req = min(
                available,
                key=lambda r: (
                    {"P1": 0, "P2": 1, "P3": 2}[r.priority],
                    r.request_time_h + r.deadline_h,
                    r.request_time_h,
                    r.request_id,
                ),
            )
            option = choose_common_bank(scenario, req, current_time_h)
            reason = "Mayor prioridad; luego menor vencimiento de plazo"
        elif strategy == "utility":
            best = None
            for candidate in available:
                for bank, distance, delivery_h in feasible_banks(
                    scenario, candidate, current_time_h
                ):
                    cand_components = utility_components(
                        scenario, candidate, bank, distance, weights, current_time_h
                    )
                    cand_score = cand_components["utility"]
                    item = (
                        cand_score,
                        -distance,
                        -candidate.request_time_h,
                        candidate.request_id,
                        candidate,
                        bank,
                        distance,
                        delivery_h,
                        cand_components,
                    )
                    if best is None or item[:4] > best[:4]:
                        best = item
            if best is not None:
                score, _, _, _, req, bank, distance, delivery_h, components = best
                option = (bank, distance, delivery_h)
                reason = "Mayor utilidad entre solicitudes y bancos factibles"
            else:
                req = min(available, key=lambda r: (r.request_time_h, r.request_id))
                reason = "Sin stock vigente factible"
        else:
            raise ValueError(f"Estrategia desconocida: {strategy}")

        pending.remove(req)
        due_time_h = req.request_time_h + req.deadline_h

        if option is None:
            deliveries.append(
                {
                    "request_id": req.request_id,
                    "hospital_id": req.hospital_id,
                    "blood_type": req.blood_type,
                    "units": req.units,
                    "priority": req.priority,
                    "status": "NO_ATENDIDA",
                    "bank_id": None,
                    "dispatch_time_h": round(current_time_h, 2),
                    "arrival_time_h": None,
                    "due_time_h": round(due_time_h, 2),
                    "distance_km": None,
                    "delivery_h": None,
                    "on_time": False,
                    "utility": None,
                    "decision_reason": reason,
                    "batches": "",
                }
            )
            continue

        bank, distance, delivery_h = option
        if strategy == "utility" and score is None:
            components = utility_components(
                scenario, req, bank, distance, weights, current_time_h
            )
            score = components["utility"]

        dispatch_time_h = current_time_h
        used_batches = allocate_fefo(
            bank, req.blood_type, req.units, current_time_h=dispatch_time_h
        )
        if not used_batches:
            status = "NO_ATENDIDA"
            on_time = False
            arrival_time_h = None
        else:
            status = "ATENDIDA"
            arrival_time_h = dispatch_time_h + delivery_h
            on_time = arrival_time_h <= due_time_h + 1e-9
            current_time_h = arrival_time_h

        row = {
            "request_id": req.request_id,
            "hospital_id": req.hospital_id,
            "blood_type": req.blood_type,
            "units": req.units,
            "priority": req.priority,
            "status": status,
            "bank_id": bank.bank_id if status == "ATENDIDA" else None,
            "dispatch_time_h": round(dispatch_time_h, 2),
            "arrival_time_h": round(arrival_time_h, 2) if arrival_time_h is not None else None,
            "due_time_h": round(due_time_h, 2),
            "distance_km": round(distance, 2) if status == "ATENDIDA" else None,
            "delivery_h": round(delivery_h, 2) if status == "ATENDIDA" else None,
            "on_time": bool(on_time),
            "utility": round(score, 4) if score is not None else None,
            "decision_reason": reason,
            "batches": ", ".join(f"{b}:{u}" for b, u, _ in used_batches),
        }
        if components:
            row.update({k: round(v, 4) for k, v in components.items() if k != "utility"})
        deliveries.append(row)

    elapsed_ms = (time.perf_counter() - started) * 1000.0
    df = pd.DataFrame(deliveries)

    p1_total = sum(1 for r in source_scenario.requests if r.priority == "P1")
    served = int((df["status"] == "ATENDIDA").sum()) if not df.empty else 0
    p1_on_time = int(
        (
            (df["priority"] == "P1")
            & (df["status"] == "ATENDIDA")
            & (df["on_time"])
        ).sum()
    ) if not df.empty else 0

    # Desperdicio: unidades que quedan sin usar y vencen dentro del horizonte del escenario.
    remaining_waste = sum(
        max(0, batch.units)
        for bank in scenario.banks
        for batch in bank.batches
        if batch.expires_in_h <= scenario.horizon_h
    )

    served_df = df[df["status"] == "ATENDIDA"] if not df.empty else df
    metrics = {
        "strategy": strategy,
        "p1_on_time_rate": round(100.0 * p1_on_time / p1_total, 2) if p1_total else 0.0,
        "p1_on_time": p1_on_time,
        "p1_total": p1_total,
        "served_requests": served,
        "served_rate": round(100.0 * served / len(source_scenario.requests), 2)
        if source_scenario.requests
        else 0.0,
        "unserved_requests": len(source_scenario.requests) - served,
        "avg_delivery_h": round(float(served_df["delivery_h"].mean()), 3) if served else 0.0,
        "total_distance_km": round(float(served_df["distance_km"].sum()), 2) if served else 0.0,
        "wasted_units": int(remaining_waste),
        "cpu_ms": round(elapsed_ms, 3),
    }
    return metrics, df


def scenario_stock_table(scenario: Scenario) -> pd.DataFrame:
    rows = []
    for bank in scenario.banks:
        for blood_type in BLOOD_TYPES:
            units = available_units(bank, blood_type, current_time_h=0.0)
            if units:
                rows.append({"Banco": bank.name, "Tipo": blood_type, "Unidades": units})
    return pd.DataFrame(rows)


def request_table(scenario: Scenario) -> pd.DataFrame:
    return pd.DataFrame(
        [
            {
                "Solicitud": r.request_id,
                "Hospital": r.hospital_id,
                "Tipo": r.blood_type,
                "Unidades": r.units,
                "Prioridad": r.priority,
                "Hora": r.request_time_h,
                "Plazo_h": r.deadline_h,
                "Límite_h": round(r.request_time_h + r.deadline_h, 2),
            }
            for r in scenario.requests
        ]
    )
