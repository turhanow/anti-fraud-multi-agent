from __future__ import annotations

from dataclasses import dataclass
from typing import List, Optional

from anti_fraud.agents.merchant.config import (
    BOOST_HIGH_RISK_CATEGORY,
    BOOST_HIGH_RISK_MERCHANT_FLAG,
    BOOST_ONLINE_HIGH_AMOUNT,
    BOOST_SUSPICIOUS_NAME,
    HIGH_RISK_CATEGORIES,
    RISK_SCORE_HIGH,
    RISK_SCORE_MEDIUM,
)
from anti_fraud.models.transaction import Transaction


@dataclass(frozen=True)
class MerchantRuleContext:
    category: str
    is_online: Optional[bool]
    merchant_name: str
    high_amount_threshold: float
    suspicious_name: bool


@dataclass(frozen=True)
class RuleResult:
    score_delta: float
    reasons: List[str]
    features: List[str]


class MerchantRule:
    def apply(self, transaction: Transaction, ctx: MerchantRuleContext) -> RuleResult:
        raise NotImplementedError


class MerchantRiskScoreRule(MerchantRule):
    def apply(self, transaction: Transaction, ctx: MerchantRuleContext) -> RuleResult:
        if transaction.merchant_risk_score is None:
            return RuleResult(0.0, [], [])
        reasons: List[str] = []
        score_delta = float(transaction.merchant_risk_score)
        if transaction.merchant_risk_score >= RISK_SCORE_HIGH:
            reasons.append(
                f"High merchant risk score ({transaction.merchant_risk_score:.2f})"
            )
        elif transaction.merchant_risk_score >= RISK_SCORE_MEDIUM:
            reasons.append(
                f"Medium merchant risk score ({transaction.merchant_risk_score:.2f})"
            )
        return RuleResult(score_delta, reasons, ["merchant_risk_score"])


class HighRiskMerchantFlagRule(MerchantRule):
    def apply(self, transaction: Transaction, ctx: MerchantRuleContext) -> RuleResult:
        if transaction.high_risk_merchant is not True:
            return RuleResult(0.0, [], [])
        return RuleResult(
            BOOST_HIGH_RISK_MERCHANT_FLAG,
            ["High-risk merchant flag"],
            ["high_risk_merchant"],
        )


class HighRiskCategoryRule(MerchantRule):
    def apply(self, transaction: Transaction, ctx: MerchantRuleContext) -> RuleResult:
        if not ctx.category:
            return RuleResult(0.0, [], [])
        if ctx.category not in HIGH_RISK_CATEGORIES:
            return RuleResult(0.0, [], ["merchant_category"])
        return RuleResult(
            BOOST_HIGH_RISK_CATEGORY,
            [f"High-risk category: {transaction.merchant_category}"],
            ["merchant_category"],
        )


class OnlineHighAmountRule(MerchantRule):
    def apply(self, transaction: Transaction, ctx: MerchantRuleContext) -> RuleResult:
        if ctx.is_online is not True:
            return RuleResult(0.0, [], [])
        features: List[str] = []
        if transaction.channel is not None:
            features.append("channel")
        if transaction.merchant_type is not None:
            features.append("merchant_type")
        if transaction.card_present is not None:
            features.append("card_present")
        if transaction.amount is None or transaction.amount < ctx.high_amount_threshold:
            return RuleResult(0.0, [], features)
        features.append("amount")
        return RuleResult(
            BOOST_ONLINE_HIGH_AMOUNT,
            [f"Online high-amount transaction (>= {ctx.high_amount_threshold:.0f})"],
            features,
        )


class SuspiciousNameRule(MerchantRule):
    def apply(self, transaction: Transaction, ctx: MerchantRuleContext) -> RuleResult:
        if not ctx.merchant_name:
            return RuleResult(0.0, [], [])
        if not ctx.suspicious_name:
            return RuleResult(0.0, [], ["merchant"])
        return RuleResult(
            BOOST_SUSPICIOUS_NAME,
            [f"Suspicious merchant name: {transaction.merchant}"],
            ["merchant"],
        )


def default_rules() -> List[MerchantRule]:
    return [
        MerchantRiskScoreRule(),
        HighRiskMerchantFlagRule(),
        HighRiskCategoryRule(),
        OnlineHighAmountRule(),
        SuspiciousNameRule(),
    ]
