from __future__ import annotations

from dataclasses import dataclass
from typing import List


@dataclass(frozen=True)
class AgentResult:
    agent: str
    score: float
    risk_level: str
    explanation: str
    features_used: List[str]
    reasons: List[str]
