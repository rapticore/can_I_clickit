from app.models.recovery import ThreatCategory, TriageAnswer


DIRECT_MAPPINGS = {
    "q1_password": ThreatCategory.CREDENTIAL_THEFT,
    "q1_financial": ThreatCategory.FINANCIAL_FRAUD,
    "q1_download": ThreatCategory.MALWARE_DOWNLOAD,
    "q1_personal": ThreatCategory.IDENTITY_THEFT,
    "q1_money": ThreatCategory.GIFT_CARD_WIRE,
    "q1_remote": ThreatCategory.REMOTE_ACCESS,
    "q1_threat": ThreatCategory.BLACKMAIL_SEXTORTION,
    "q1_ransom": ThreatCategory.RANSOMWARE_EXTORTION,
    "q1_invest": ThreatCategory.PIG_BUTCHERING,
    "q1_unknown": ThreatCategory.GENERAL_UNKNOWN,
    "q2_nothing": ThreatCategory.GENERAL_UNKNOWN,
    "q2_entered_pw": ThreatCategory.CREDENTIAL_THEFT,
    "q2_entered_card": ThreatCategory.FINANCIAL_FRAUD,
    "q2_downloaded": ThreatCategory.MALWARE_DOWNLOAD,
    "q2_not_sure": ThreatCategory.GENERAL_UNKNOWN,
}


def classify_triage(answers: list[TriageAnswer]) -> ThreatCategory:
    """Classify threat category from triage answers using direct mapping."""
    for answer in reversed(answers):
        category = DIRECT_MAPPINGS.get(answer.selected_option_id)
        if category:
            return category
    return ThreatCategory.GENERAL_UNKNOWN
