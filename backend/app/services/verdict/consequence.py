from app.models.verdict import CONSEQUENCE_TEMPLATES


def generate_consequence(scam_pattern: str | None) -> str:
    if scam_pattern and scam_pattern in CONSEQUENCE_TEMPLATES:
        return CONSEQUENCE_TEMPLATES[scam_pattern]
    return CONSEQUENCE_TEMPLATES["generic"]
