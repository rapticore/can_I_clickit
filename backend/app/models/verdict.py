from __future__ import annotations

from pydantic import BaseModel, Field

from app.models.scan import ConfidenceLevel, SignalResult, ThreatLevel


class VerdictInput(BaseModel):
    """Aggregated signals fed into the verdict engine."""

    signals: list[SignalResult] = []
    raw_score: float = Field(ge=0.0, le=100.0, default=50.0)
    analysis_tier: str = "fast_path"
    detected_pattern: str | None = None
    content_snippet: str = ""


class VerdictOutput(BaseModel):
    threat_level: ThreatLevel
    confidence: ConfidenceLevel
    confidence_score: float = Field(ge=0.0, le=100.0)
    verdict_summary: str
    consequence_warning: str
    safe_action_suggestion: str
    explanation: str
    scam_pattern: str | None = None


CONSEQUENCE_TEMPLATES: dict[str, str] = {
    "phishing": "If this is a phishing site and you enter your password, someone could access your email and any accounts linked to it.",
    "financial_fraud": "If you share bank or credit card details, unauthorized charges could appear on your account and recovery may take weeks.",
    "gift_card_scam": "If you send money via gift cards, it cannot be recovered. Legitimate companies never request payment this way.",
    "sextortion": "This looks like a sextortion scam. These emails are almost always bluffs — the sender likely does not have what they claim. Do not pay or respond.",
    "pig_butchering": "This person may be building trust to eventually ask you to invest money. This pattern matches a common romance-investment scam. Never invest through a platform recommended by someone you have only met online.",
    "ransomware_bluff": "This email claims your files are encrypted, but many of these are bluff emails. Check whether you can still open your files before taking any action.",
    "identity_theft": "If you share personal information like your SSN or date of birth, it could be used to open accounts in your name or file fraudulent tax returns.",
    "malware": "If you download or open this file, it could install software that monitors your activity, steals your data, or locks your files.",
    "impersonation": "This message appears to impersonate someone you know. Before responding or sending money, contact them directly through a known phone number.",
    "generic": "If this is a scam and you proceed, you could lose money, expose personal information, or compromise your accounts.",
}

SAFE_ACTION_TEMPLATES: dict[str, str] = {
    "banking": "If this claims to be your bank, open your banking app directly instead of clicking the link.",
    "shipping": "If this claims a package is waiting, go to the carrier's website by typing the URL yourself.",
    "family": "If someone claims to be a family member, call them at their known phone number to verify.",
    "government": "If this claims to be from a government agency, visit the official website directly or call the number listed on your official documents.",
    "tech_support": "Legitimate tech companies do not call or message you about problems with your device. Close the message and contact support through the official website.",
    "invoice": "If you received an unexpected invoice, log into the service directly to check your account rather than clicking any links in the message.",
    "generic": "Verify this message by contacting the sender through a channel you trust, such as a phone number you already have saved.",
}
