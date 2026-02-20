import json
from pathlib import Path

import structlog

from app.models.recovery import (
    QuickDialContact,
    RecoveryChecklist,
    RecoveryStep,
    ThreatCategory,
    TriageAnswer,
    TriageQuestion,
    TriageOption,
    UrgencyLevel,
)

logger = structlog.get_logger()

LIBRARY_PATH = Path(__file__).resolve().parents[4] / "docs" / "recovery_content" / "recovery_library.json"


class RecoveryEngine:
    """Generates personalized recovery checklists from triage answers.

    Uses the recovery content library (10 categories) to produce
    step-by-step guidance tailored to the incident type.
    """

    def __init__(self):
        self._library: dict | None = None

    def _load_library(self) -> dict:
        if self._library is None:
            try:
                with open(LIBRARY_PATH) as f:
                    self._library = json.load(f)
            except FileNotFoundError:
                logger.error("recovery_library_not_found", path=str(LIBRARY_PATH))
                self._library = {"categories": {}, "triage_questions": []}
        return self._library

    def classify_from_triage(self, answers: list[TriageAnswer]) -> ThreatCategory:
        library = self._load_library()
        questions = library.get("triage_questions", [])

        for answer in answers:
            for question in questions:
                if question["id"] == answer.question_id:
                    for option in question["options"]:
                        if option["id"] == answer.selected_option_id and option.get("maps_to"):
                            try:
                                return ThreatCategory(option["maps_to"])
                            except ValueError:
                                continue

        return ThreatCategory.GENERAL_UNKNOWN

    def get_checklist(self, category: ThreatCategory) -> RecoveryChecklist:
        library = self._load_library()
        categories = library.get("categories", {})

        cat_data = categories.get(category.value)
        if not cat_data:
            return self._default_checklist(category)

        steps = [
            RecoveryStep(
                step_number=step["step_number"],
                title=step["title"],
                description=step["description"],
                help_detail=step.get("help_detail", ""),
                action_type=step.get("action_type", "info"),
                action_data=step.get("action_data"),
            )
            for step in cat_data["steps"]
        ]

        contacts = [
            QuickDialContact(
                name=c["name"],
                phone=c["phone"],
                description=c.get("description", ""),
            )
            for c in cat_data.get("quick_dial_contacts", [])
        ]

        try:
            urgency = UrgencyLevel(cat_data["urgency"])
        except ValueError:
            urgency = UrgencyLevel.MEDIUM

        return RecoveryChecklist(
            category=category,
            urgency=urgency,
            title=cat_data["title"],
            opening_message=cat_data.get("opening_message", "Don't worry — let's fix this together."),
            steps=steps,
            quick_dial_contacts=contacts,
        )

    def get_triage_questions(self) -> list[dict]:
        library = self._load_library()
        return library.get("triage_questions", [])

    @staticmethod
    def _default_checklist(category: ThreatCategory) -> RecoveryChecklist:
        return RecoveryChecklist(
            category=category,
            urgency=UrgencyLevel.MEDIUM,
            title="General Safety Steps",
            steps=[
                RecoveryStep(
                    step_number=1,
                    title="Change your most important passwords",
                    description="Start with your email, then banking and financial accounts, then social media.",
                    help_detail="Use a unique, strong password for each account.",
                ),
                RecoveryStep(
                    step_number=2,
                    title="Enable two-factor authentication",
                    description="Turn on 2FA on your email and banking accounts.",
                ),
                RecoveryStep(
                    step_number=3,
                    title="Monitor your accounts",
                    description="Check your email, bank, and social media for unusual activity over the next few weeks.",
                ),
            ],
        )
