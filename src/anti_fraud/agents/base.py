from __future__ import annotations

from abc import ABC, abstractmethod

from anti_fraud.models.agent_result import AgentResult
from anti_fraud.models.transaction import Transaction


class BaseAgent(ABC):
    name: str

    @abstractmethod
    def analyze(self, transaction: Transaction) -> AgentResult:
        raise NotImplementedError
