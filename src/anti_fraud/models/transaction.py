from __future__ import annotations

from dataclasses import dataclass
from typing import Optional


@dataclass(frozen=True)
class Transaction:
    transaction_id: Optional[str] = None
    customer_id: Optional[str] = None
    timestamp: Optional[str] = None

    amount: Optional[float] = None
    currency: Optional[str] = None
    card_type: Optional[str] = None
    card_present: Optional[bool] = None

    merchant: Optional[str] = None
    merchant_category: Optional[str] = None
    merchant_type: Optional[str] = None
    merchant_risk_score: Optional[float] = None
    high_risk_merchant: Optional[bool] = None

    country: Optional[str] = None
    city: Optional[str] = None

    device_type: Optional[str] = None
    device_fingerprint: Optional[str] = None
    channel: Optional[str] = None

    account_age: Optional[int] = None
    typical_spending_range: Optional[str] = None
    preferred_devices: Optional[str] = None
    fraud_protection_enabled: Optional[bool] = None
