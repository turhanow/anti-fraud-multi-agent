import pytest

from anti_fraud.agents.merchant.agent import MerchantAgent
from anti_fraud.models.transaction import Transaction


pytestmark = pytest.mark.integration

def test_agent_low_risk_default_reason():
    agent = MerchantAgent()
    transaction = Transaction()

    result = agent.analyze(transaction)

    assert result.score == 0.0
    assert result.risk_level == "LOW"
    assert result.reasons == ["No specific merchant risk signals"]
    assert result.features_used == []


def test_agent_compound_high_risk_capped_and_explained():
    agent = MerchantAgent()
    transaction = Transaction(
        merchant_risk_score=0.6,
        high_risk_merchant=True,
        merchant_category="gambling",
        channel="web",
        amount=250000,
    )

    result = agent.analyze(transaction)

    expected_reasons = [
        "Medium merchant risk score (0.60)",
        "High-risk merchant flag",
        "High-risk category: gambling",
        "Online high-amount transaction (>= 200000)",
    ]
    expected_features = [
        "amount",
        "channel",
        "high_risk_merchant",
        "merchant_category",
        "merchant_risk_score",
    ]

    assert result.score == 1.0  # capped at 1.0
    assert result.risk_level == "HIGH"
    assert result.reasons == expected_reasons
    assert result.explanation == "; ".join(expected_reasons)
    assert result.features_used == expected_features


def test_agent_medium_risk_boundary_and_features():
    agent = MerchantAgent()
    transaction = Transaction(
        merchant_risk_score=0.4,  # boundary for MEDIUM
        merchant_category="grocery",
        channel="web",
        amount=250000,
    )

    result = agent.analyze(transaction)

    expected_reasons = [
        "Online high-amount transaction (>= 176526)",
    ]
    expected_features = ["amount", "channel", "merchant_category", "merchant_risk_score"]

    assert result.score == pytest.approx(0.4 + 0.15, rel=1e-6)
    assert result.risk_level == "MEDIUM"
    assert result.reasons == expected_reasons
    assert result.explanation == "; ".join(expected_reasons)
    assert result.features_used == expected_features


def test_agent_normalizes_category_and_stays_low_risk():
    agent = MerchantAgent()
    transaction = Transaction(
        merchant="Local Grocery",
        merchant_category="groceries",  # will normalize to "grocery"
        channel="web",
        amount=50000,
    )

    result = agent.analyze(transaction)

    assert result.score == 0.0
    assert result.risk_level == "LOW"
    assert result.reasons == ["No specific merchant risk signals"]
    assert "merchant_category" in result.features_used
