"""Interfaces simples de las tres estrategias del avance."""

from typing import Dict, Optional, Tuple

import pandas as pd

from models import Scenario
from simulation import simulate_strategy


DEFAULT_WEIGHTS = {
    "priority": 0.45,
    "urgency": 0.25,
    "expiry": 0.15,
    "transport": 0.10,
    "stock": 0.05,
}


def fifo_agent(scenario: Scenario):
    return simulate_strategy(scenario, "fifo")


def goal_agent(scenario: Scenario):
    return simulate_strategy(scenario, "goal")


def utility_agent(scenario: Scenario, weights: Optional[Dict[str, float]] = None):
    return simulate_strategy(scenario, "utility", weights or DEFAULT_WEIGHTS)
