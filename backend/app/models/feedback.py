from __future__ import annotations

from enum import Enum
from datetime import datetime

from pydantic import BaseModel, Field, model_validator


class FeedbackVerdict(str, Enum):
    CORRECT = "correct"
    INCORRECT_FALSE_POSITIVE = "incorrect_false_positive"
    INCORRECT_FALSE_NEGATIVE = "incorrect_false_negative"


class FeedbackRequest(BaseModel):
    scan_id: str
    user_verdict: FeedbackVerdict | None = None
    accurate: bool | None = None
    is_helpful: bool | None = None
    comment: str = ""

    @model_validator(mode="after")
    def normalize_verdict(self) -> "FeedbackRequest":
        if self.user_verdict is not None:
            return self
        source_flag = self.accurate if self.accurate is not None else self.is_helpful
        if source_flag is None:
            self.user_verdict = FeedbackVerdict.CORRECT
        elif source_flag:
            self.user_verdict = FeedbackVerdict.CORRECT
        else:
            self.user_verdict = FeedbackVerdict.INCORRECT_FALSE_NEGATIVE
        return self


class FeedbackResponse(BaseModel):
    feedback_id: str
    scan_id: str
    acknowledged: bool = True
    message: str = "Thank you for your feedback. It helps us improve."
    created_at: datetime = Field(default_factory=datetime.utcnow)
