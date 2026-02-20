from __future__ import annotations

from enum import Enum
from datetime import datetime

from pydantic import AliasChoices, BaseModel, Field, model_validator


class ScanType(str, Enum):
    TEXT = "text"
    URL = "url"
    EMAIL = "email"
    PHONE = "phone"
    SMS = "sms"
    SCREENSHOT = "screenshot"
    QR_CODE = "qr_code"
    QR = "qr"


class ScanRequest(BaseModel):
    content: str | None = Field(None, description="Text or URL to analyze")
    scan_type: ScanType = Field(
        ScanType.TEXT,
        description="Type of content being scanned",
        validation_alias=AliasChoices("scan_type", "type"),
    )
    image_base64: str | None = Field(None, description="Base64-encoded image for screenshot/QR scans")
    language: str = Field("en", description="Content language hint")
    metadata: dict | None = Field(None, description="Optional client metadata (legacy/mobile/extension)")

    @model_validator(mode="after")
    def normalize_scan_type(self) -> "ScanRequest":
        if self.scan_type in {ScanType.EMAIL, ScanType.PHONE, ScanType.SMS}:
            self.scan_type = ScanType.TEXT
        elif self.scan_type == ScanType.QR:
            self.scan_type = ScanType.QR_CODE
        return self


class ThreatLevel(str, Enum):
    SAFE = "safe"
    SUSPICIOUS = "suspicious"
    DANGEROUS = "dangerous"


class ConfidenceLevel(str, Enum):
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"


class SignalSource(str, Enum):
    BLOCKLIST = "blocklist"
    DOMAIN_AGE = "domain_age"
    HEURISTIC = "heuristic"
    ML_CLASSIFIER = "ml_classifier"
    INTENT_DETECTION = "intent_detection"
    LLM_REASONING = "llm_reasoning"
    SSL_CHECK = "ssl_check"
    REDIRECT_ANALYSIS = "redirect_analysis"
    TYPOSQUATTING = "typosquatting"
    CAMPAIGN_MATCH = "campaign_match"


class SignalResult(BaseModel):
    source: SignalSource
    score: float = Field(ge=0.0, le=100.0)
    detail: str = ""


class ScanResult(BaseModel):
    scan_id: str
    scan_type: ScanType
    threat_level: ThreatLevel
    confidence: ConfidenceLevel
    confidence_score: float = Field(ge=0.0, le=100.0)
    verdict_summary: str
    consequence_warning: str
    safe_action_suggestion: str
    explanation: str
    signals: list[SignalResult] = Field(default_factory=list)
    scam_pattern: str | None = None
    analysis_tier: str = "fast_path"
    latency_ms: int = 0
    disclaimer: str = "This analysis is our best assessment based on available signals. Always verify directly with the sender if you are unsure."
    created_at: datetime = Field(default_factory=datetime.utcnow)

    # Legacy/mobile/extension compatibility fields.
    id: str | None = None
    verdict: str | None = None
    summary: str | None = None
    plain_language_summary: str | None = None
    safe_action: str | None = None
    consequences: str | None = None
    scanned_at: datetime | None = None

    @model_validator(mode="after")
    def hydrate_compat_fields(self) -> "ScanResult":
        self.id = self.id or self.scan_id
        self.verdict = self.verdict or self.threat_level.value
        self.summary = self.summary or self.verdict_summary
        self.plain_language_summary = self.plain_language_summary or self.explanation
        self.safe_action = self.safe_action or self.safe_action_suggestion
        self.consequences = self.consequences or self.consequence_warning
        self.scanned_at = self.scanned_at or self.created_at
        return self


class ScanHistoryItem(BaseModel):
    scan_id: str
    scan_type: ScanType
    threat_level: ThreatLevel
    confidence: ConfidenceLevel
    verdict_summary: str
    created_at: datetime
