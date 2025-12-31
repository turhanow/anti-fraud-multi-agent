import pytest

from anti_fraud.agents.merchant.config import HIGH_AMOUNT_THRESHOLD
from anti_fraud.agents.merchant.rules import (
    HighRiskCategoryRule,
    HighRiskMerchantFlagRule,
    MerchantRiskScoreRule,
    MerchantRuleContext,
    OnlineHighAmountRule,
    SuspiciousNameRule,
)
from anti_fraud.models.transaction import Transaction

pytestmark = pytest.mark.unit


def make_context(
    *,
    category: str = "",
    is_online=None,
    merchant_name: str = "",
    high_amount_threshold: float = HIGH_AMOUNT_THRESHOLD,
    suspicious_name: bool = False,
) -> MerchantRuleContext:
    return MerchantRuleContext(
        category=category,
        is_online=is_online,
        merchant_name=merchant_name,
        high_amount_threshold=high_amount_threshold,
        suspicious_name=suspicious_name,
    )


class TestMerchantRiskScoreRule:
    def test_no_score(self):
        rule = MerchantRiskScoreRule()
        transaction = Transaction()
        context = make_context()

        result = rule.apply(transaction, context)

        assert result.score_delta == 0.0
        assert result.reasons == []
        assert result.features == []

    def test_low_score_no_reason(self):
        rule = MerchantRiskScoreRule()
        transaction = Transaction(merchant_risk_score=0.2)
        context = make_context()

        result = rule.apply(transaction, context)

        assert result.score_delta == 0.2
        assert result.reasons == []
        assert result.features == ["merchant_risk_score"]

    def test_medium_score_reason(self):
        rule = MerchantRiskScoreRule()
        transaction = Transaction(merchant_risk_score=0.5)
        context = make_context()

        result = rule.apply(transaction, context)

        assert result.score_delta == 0.5
        assert result.reasons == ["Medium merchant risk score (0.50)"]
        assert result.features == ["merchant_risk_score"]

    def test_high_score_reason(self):
        rule = MerchantRiskScoreRule()
        transaction = Transaction(merchant_risk_score=0.85)
        context = make_context()

        result = rule.apply(transaction, context)

        assert result.score_delta == 0.85
        assert result.reasons == ["High merchant risk score (0.85)"]
        assert result.features == ["merchant_risk_score"]


class TestHighRiskMerchantFlagRule:
    def test_flag_true(self):
        rule = HighRiskMerchantFlagRule()
        transaction = Transaction(high_risk_merchant=True)
        context = make_context()

        result = rule.apply(transaction, context)

        assert result.score_delta > 0
        assert "High-risk merchant flag" in result.reasons
        assert result.features == ["high_risk_merchant"]

    @pytest.mark.parametrize("flag", [False, None])
    def test_flag_not_true(self, flag):
        rule = HighRiskMerchantFlagRule()
        transaction = Transaction(high_risk_merchant=flag)
        context = make_context()

        result = rule.apply(transaction, context)

        assert result.score_delta == 0.0
        assert result.reasons == []
        assert result.features == []


class TestHighRiskCategoryRule:
    def test_no_category(self):
        rule = HighRiskCategoryRule()
        transaction = Transaction(merchant_category=None)
        context = make_context(category="")

        result = rule.apply(transaction, context)

        assert result.score_delta == 0.0
        assert result.reasons == []
        assert result.features == []

    def test_not_high_risk_category(self):
        rule = HighRiskCategoryRule()
        transaction = Transaction(merchant_category="grocery")
        context = make_context(category="grocery")

        result = rule.apply(transaction, context)

        assert result.score_delta == 0.0
        assert result.reasons == []
        assert result.features == ["merchant_category"]

    def test_high_risk_category(self):
        rule = HighRiskCategoryRule()
        transaction = Transaction(merchant_category="gambling")
        context = make_context(category="gambling")

        result = rule.apply(transaction, context)

        assert result.score_delta > 0
        assert result.reasons == ["High-risk category: gambling"]
        assert result.features == ["merchant_category"]

    def test_high_risk_category_with_normalized_ctx(self):
        rule = HighRiskCategoryRule()
        # raw category in transaction, normalized category in context
        transaction = Transaction(merchant_category="GAMBLING")
        context = make_context(category="gambling")

        result = rule.apply(transaction, context)

        assert result.score_delta > 0
        assert result.reasons == ["High-risk category: GAMBLING"]
        assert result.features == ["merchant_category"]


class TestOnlineHighAmountRule:
    def test_offline(self):
        rule = OnlineHighAmountRule()
        transaction = Transaction(amount=300000, channel="pos")
        context = make_context(is_online=False, high_amount_threshold=200000)

        result = rule.apply(transaction, context)

        assert result.score_delta == 0.0
        assert result.reasons == []
        assert result.features == []

    def test_online_amount_missing(self):
        rule = OnlineHighAmountRule()
        transaction = Transaction(amount=None, channel="web", card_present=None)
        context = make_context(is_online=True, high_amount_threshold=200000)

        result = rule.apply(transaction, context)

        assert result.score_delta == 0.0
        assert result.reasons == []
        assert set(result.features) == {"channel"}

    def test_online_below_threshold(self):
        rule = OnlineHighAmountRule()
        transaction = Transaction(amount=150000, channel="web", card_present=False)
        context = make_context(is_online=True, high_amount_threshold=200000)

        result = rule.apply(transaction, context)

        assert result.score_delta == 0.0
        assert result.reasons == []
        assert set(result.features) == {"channel", "card_present"}

    def test_online_above_threshold(self):
        rule = OnlineHighAmountRule()
        transaction = Transaction(amount=250000, channel="web", merchant_type=None, card_present=None)
        context = make_context(is_online=True, high_amount_threshold=200000)

        result = rule.apply(transaction, context)

        assert result.score_delta > 0
        assert result.reasons == ["Online high-amount transaction (>= 200000)"]
        assert set(result.features) == {"channel", "amount"}

    def test_online_status_unknown_returns_neutral(self):
        rule = OnlineHighAmountRule()
        transaction = Transaction(amount=300000, channel=None, merchant_type=None, card_present=None)
        context = make_context(is_online=None, high_amount_threshold=200000)

        result = rule.apply(transaction, context)

        assert result.score_delta == 0.0
        assert result.reasons == []
        assert result.features == []

    def test_online_above_threshold_custom_category_limit(self):
        rule = OnlineHighAmountRule()
        transaction = Transaction(amount=300000, channel="web", merchant_type="online", card_present=False)
        context = make_context(is_online=True, high_amount_threshold=150000)

        result = rule.apply(transaction, context)

        assert result.score_delta > 0
        assert result.reasons == ["Online high-amount transaction (>= 150000)"]
        assert set(result.features) == {"channel", "merchant_type", "card_present", "amount"}


class TestSuspiciousNameRule:
    def test_no_name(self):
        rule = SuspiciousNameRule()
        transaction = Transaction(merchant=None)
        context = make_context(merchant_name="", suspicious_name=False)

        result = rule.apply(transaction, context)

        assert result.score_delta == 0.0
        assert result.reasons == []
        assert result.features == []

    def test_not_suspicious_name(self):
        rule = SuspiciousNameRule()
        transaction = Transaction(merchant="example store")
        context = make_context(merchant_name="example store", suspicious_name=False)

        result = rule.apply(transaction, context)

        assert result.score_delta == 0.0
        assert result.reasons == []
        assert result.features == ["merchant"]

    def test_suspicious_name(self):
        rule = SuspiciousNameRule()
        transaction = Transaction(merchant="12345")
        context = make_context(merchant_name="12345", suspicious_name=True)

        result = rule.apply(transaction, context)

        assert result.score_delta > 0
        assert result.reasons == ["Suspicious merchant name: 12345"]
        assert result.features == ["merchant"]
