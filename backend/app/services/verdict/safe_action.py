from app.models.verdict import SAFE_ACTION_TEMPLATES

PATTERN_TO_ACTION_CATEGORY = {
    "phishing": "banking",
    "financial_fraud": "banking",
    "impersonation": "family",
    "identity_theft": "government",
    "malware": "tech_support",
    "gift_card_scam": "invoice",
    "sextortion": "generic",
    "pig_butchering": "generic",
    "ransomware_bluff": "generic",
}


def generate_safe_action(scam_pattern: str | None) -> str:
    category = PATTERN_TO_ACTION_CATEGORY.get(scam_pattern or "", "generic")
    return SAFE_ACTION_TEMPLATES.get(category, SAFE_ACTION_TEMPLATES["generic"])
