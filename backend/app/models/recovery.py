from __future__ import annotations

from enum import Enum
from datetime import datetime

from pydantic import BaseModel, Field, model_validator


class ThreatCategory(str, Enum):
    CREDENTIAL_THEFT = "credential_theft"
    FINANCIAL_FRAUD = "financial_fraud"
    IDENTITY_THEFT = "identity_theft"
    MALWARE_DOWNLOAD = "malware_download"
    GIFT_CARD_WIRE = "gift_card_wire"
    REMOTE_ACCESS = "remote_access"
    GENERAL_UNKNOWN = "general_unknown"
    BLACKMAIL_SEXTORTION = "blackmail_sextortion"
    RANSOMWARE_EXTORTION = "ransomware_extortion"
    PIG_BUTCHERING = "pig_butchering"


class UrgencyLevel(str, Enum):
    CRITICAL = "critical"
    HIGH = "high"
    MEDIUM = "medium"


class TriageQuestion(BaseModel):
    id: str
    question: str
    options: list[TriageOption]


class TriageOption(BaseModel):
    id: str
    label: str
    maps_to: ThreatCategory | None = None


class TriageRequest(BaseModel):
    answers: list[TriageAnswerSubmission]

    def normalized_answers(self) -> list[TriageAnswer]:
        normalized: list[TriageAnswer] = []
        for answer in self.answers:
            if answer.selected_option_id:
                normalized.append(
                    TriageAnswer(
                        question_id=answer.question_id,
                        selected_option_id=answer.selected_option_id,
                    )
                )
                continue
            if answer.answer_ids:
                first = next((value for value in answer.answer_ids if value), None)
                if first:
                    normalized.append(
                        TriageAnswer(
                            question_id=answer.question_id,
                            selected_option_id=first,
                        )
                    )
        return normalized


class TriageAnswer(BaseModel):
    question_id: str
    selected_option_id: str


class TriageAnswerSubmission(BaseModel):
    question_id: str
    selected_option_id: str | None = None
    answer_ids: list[str] | None = None

    @model_validator(mode="after")
    def ensure_selection(self) -> "TriageAnswerSubmission":
        if self.selected_option_id:
            return self
        if self.answer_ids:
            first = next((value for value in self.answer_ids if value), None)
            self.selected_option_id = first
        return self


class RecoveryStep(BaseModel):
    step_number: int
    title: str
    description: str
    help_detail: str = ""
    action_type: str = "info"
    action_data: dict | None = None


class RecoveryChecklist(BaseModel):
    category: ThreatCategory
    urgency: UrgencyLevel
    title: str
    opening_message: str = "Don't worry — let's fix this together."
    steps: list[RecoveryStep]
    quick_dial_contacts: list[QuickDialContact] = []
    disclaimer: str = "This guidance is informational and not a substitute for professional security or legal advice."
    created_at: datetime = Field(default_factory=datetime.utcnow)


class QuickDialContact(BaseModel):
    name: str
    phone: str
    description: str = ""


class RecoverySession(BaseModel):
    session_id: str
    category: ThreatCategory
    steps_completed: int = 0
    total_steps: int = 0
    created_at: datetime = Field(default_factory=datetime.utcnow)
