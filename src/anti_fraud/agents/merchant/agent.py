from __future__ import annotations

from typing import List, Optional

from anti_fraud.agents.base import BaseAgent
from anti_fraud.agents.merchant.config import (
    CATEGORY_AMOUNT_THRESHOLDS,
    CATEGORY_SYNONYMS,
    HIGH_AMOUNT_THRESHOLD,
    OFFLINE_CHANNELS,
    ONLINE_CHANNELS,
    SUSPICIOUS_MERCHANT_NAMES,
)
from anti_fraud.agents.merchant.rules import (
    MerchantRule,
    MerchantRuleContext,
    default_rules,
)
from anti_fraud.models.agent_result import AgentResult
from anti_fraud.models.transaction import Transaction


class MerchantAgent(BaseAgent):
    name = "MerchantAgent"

    def __init__(self, rules: Optional[List[MerchantRule]] = None) -> None:
        self._ruleset = rules or default_rules()

    def analyze(self, transaction: Transaction) -> AgentResult:
        reasons: List[str] = []
        features_used: List[str] = []
        score = 0.0
        ctx = self._build_context(transaction)
        for rule in self._rules():
            result = rule.apply(transaction, ctx)
            if result.score_delta:
                score += result.score_delta
            if result.reasons:
                reasons.extend(result.reasons)
            if result.features:
                features_used.extend(result.features)

        score = min(score, 1.0)
        risk_level = self._risk_level(score)

        if not reasons:
            reasons.append("No specific merchant risk signals")

        explanation = "; ".join(reasons)

        return AgentResult(
            agent=self.name,
            score=score,
            risk_level=risk_level,
            explanation=explanation,
            features_used=sorted(set(features_used)),
            reasons=reasons,
        )

    @staticmethod
    def _normalize_category(category: str) -> str:
        if not category:
            return ""
        return CATEGORY_SYNONYMS.get(category, category)

    @staticmethod
    def _high_amount_threshold(category: str) -> float:
        if category:
            return CATEGORY_AMOUNT_THRESHOLDS.get(category, HIGH_AMOUNT_THRESHOLD)
        return HIGH_AMOUNT_THRESHOLD

    @staticmethod
    def _is_suspicious_name(merchant_name: str) -> bool:
        if merchant_name in SUSPICIOUS_MERCHANT_NAMES:
            return True
        compact = merchant_name.replace(" ", "")
        if compact.isdigit():
            return True
        if merchant_name in {"n/a", "na", "none"}:
            return True
        return False

    @staticmethod
    def _is_online(transaction: Transaction) -> Optional[bool]:
        channel = (transaction.channel or "").strip().lower()
        if channel:
            if channel in ONLINE_CHANNELS:
                return True
            if channel in OFFLINE_CHANNELS:
                return False
        merchant_type = (transaction.merchant_type or "").strip().lower()
        if merchant_type == "online":
            return True
        if transaction.card_present is False:
            return True
        return None

    def _build_context(self, transaction: Transaction) -> MerchantRuleContext:
        category_raw = (transaction.merchant_category or "").strip().lower()
        category = self._normalize_category(category_raw)
        merchant_name = (transaction.merchant or "").strip().lower()
        return MerchantRuleContext(
            category=category,
            is_online=self._is_online(transaction),
            merchant_name=merchant_name,
            high_amount_threshold=self._high_amount_threshold(category),
            suspicious_name=self._is_suspicious_name(merchant_name) if merchant_name else False,
        )

    def _rules(self) -> List[MerchantRule]:
        return self._ruleset

    @staticmethod
    def _risk_level(score: float) -> str:
        if score >= 0.7:
            return "HIGH"
        if score >= 0.4:
            return "MEDIUM"
        return "LOW"
