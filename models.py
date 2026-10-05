from __future__ import annotations

from dataclasses import dataclass
from typing import Dict, List

BLOOD_TYPES = ["A+", "A-", "B+", "B-", "AB+", "AB-", "O+", "O-"]
PRIORITIES = ["P1", "P2", "P3"]


@dataclass
class Batch:
    batch_id: str
    bank_id: str
    blood_type: str
    units: int
    expires_in_h: float


@dataclass
class BloodBank:
    bank_id: str
    name: str
    x: float
    y: float
    batches: List[Batch]


@dataclass
class Hospital:
    hospital_id: str
    name: str
    x: float
    y: float


@dataclass
class Request:
    request_id: str
    hospital_id: str
    blood_type: str
    units: int
    priority: str
    request_time_h: float
    deadline_h: float  # horas disponibles desde la solicitud


@dataclass
class Scenario:
    seed: int
    horizon_h: float
    banks: List[BloodBank]
    hospitals: List[Hospital]
    requests: List[Request]
    metadata: Dict[str, float]
