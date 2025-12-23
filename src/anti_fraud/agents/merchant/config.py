HIGH_RISK_CATEGORIES = {
    "gambling",
    "crypto",
    "adult",
    "gift cards",
    "digital goods",
}

CATEGORY_SYNONYMS = {
    "groceries": "grocery",
    "restaurants": "restaurant",
    "fuel": "gas",
    "gasoline": "gas",
    "traveling": "travel",
}

CATEGORY_AMOUNT_THRESHOLDS = {
    "education": 213944.92,
    "entertainment": 156762.53,
    "gas": 214728.40,
    "grocery": 176526.09,
    "healthcare": 212906.48,
    "restaurant": 143241.36,
    "retail": 322644.62,
    "travel": 472182.77,
}

SUSPICIOUS_MERCHANT_NAMES = {
    "unknown",
    "misc",
    "generic",
    "test merchant",
}

HIGH_AMOUNT_THRESHOLD = 200000.0

RISK_SCORE_HIGH = 0.8
RISK_SCORE_MEDIUM = 0.5

BOOST_HIGH_RISK_CATEGORY = 0.2
BOOST_ONLINE_HIGH_AMOUNT = 0.15
BOOST_SUSPICIOUS_NAME = 0.1
BOOST_HIGH_RISK_MERCHANT_FLAG = 0.3

ONLINE_CHANNELS = {
    "web",
    "mobile",
}

OFFLINE_CHANNELS = {
    "pos",
}
