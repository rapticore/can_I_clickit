import structlog

from app.models.scan import ScanType, SignalResult, SignalSource

logger = structlog.get_logger()

ANALYSIS_SYSTEM_PROMPT = """You are a cybersecurity analyst for "Can I Click It?", a personal AI safety assistant.
Your job is to analyze messages, URLs, and content for scam, phishing, and social engineering indicators.

Analyze the provided content and respond in JSON format with these fields:
- threat_level: "safe", "suspicious", or "dangerous"
- confidence_score: 0-100
- explanation: Plain-language explanation of your analysis (2-3 sentences, no jargon)
- consequence_warning: What could happen if this is a scam and the user proceeds (1-2 sentences)
- safe_action_suggestion: What the user should do instead (1 sentence)
- scam_pattern: The detected scam type if any (e.g., "phishing", "sextortion", "pig_butchering", "impersonation", null if safe)
- signals: List of specific indicators you found

Be conservative: when in doubt, lean toward "suspicious" rather than "safe".
Use plain language suitable for non-technical users, including seniors.
Never use security jargon without explanation."""


class LLMAnalyzer:
    """LLM-based deep analysis using Anthropic Claude.

    Only invoked when ML path confidence is < 70.
    Adds 2-3s latency but provides chain-of-thought reasoning
    and natural language explanations.
    """

    async def analyze(
        self,
        content: str,
        urls: list[str],
        scan_type: ScanType,
        prior_signals: list[SignalResult] | None = None,
    ) -> tuple[list[SignalResult], str]:
        signals: list[SignalResult] = []

        try:
            result = await self._call_anthropic(content, urls, scan_type, prior_signals)
            score = result.get("confidence_score", 50)
            signals.append(SignalResult(
                source=SignalSource.LLM_REASONING,
                score=min(float(score), 95.0),
                detail=result.get("explanation", "LLM analysis completed"),
            ))
            return signals, result.get("explanation", "")
        except Exception as exc:
            logger.error("llm_analysis_failed", error=str(exc))
            signals.append(SignalResult(
                source=SignalSource.LLM_REASONING,
                score=55.0,
                detail="LLM analysis unavailable; defaulting to suspicious",
            ))
            return signals, "Analysis system was unable to perform deep analysis. Treating as suspicious."

    async def _call_anthropic(
        self,
        content: str,
        urls: list[str],
        scan_type: ScanType,
        prior_signals: list[SignalResult] | None,
    ) -> dict:
        from app.core.config import get_settings

        settings = get_settings()

        if not settings.anthropic_api_key:
            return self._fallback_analysis(content, urls)

        import anthropic

        client = anthropic.AsyncAnthropic(api_key=settings.anthropic_api_key)

        prior_context = ""
        if prior_signals:
            prior_context = "\n\nPrior analysis signals:\n" + "\n".join(
                f"- [{s.source.value}] score={s.score}: {s.detail}" for s in prior_signals
            )

        user_message = f"""Analyze this content for scam/phishing/social engineering threats:

Content type: {scan_type.value}
Content: {content[:2000]}
URLs found: {', '.join(urls[:5]) if urls else 'None'}
{prior_context}

Respond in JSON format."""

        is_ambiguous = prior_signals and any(40 <= s.score <= 70 for s in prior_signals)
        model = settings.anthropic_model_complex if is_ambiguous else settings.anthropic_model_fast

        message = await client.messages.create(
            model=model,
            max_tokens=1024,
            system=ANALYSIS_SYSTEM_PROMPT,
            messages=[{"role": "user", "content": user_message}],
        )

        import json
        response_text = message.content[0].text
        try:
            start = response_text.find("{")
            end = response_text.rfind("}") + 1
            if start >= 0 and end > start:
                return json.loads(response_text[start:end])
        except (json.JSONDecodeError, IndexError):
            pass

        return {
            "threat_level": "suspicious",
            "confidence_score": 55,
            "explanation": response_text[:500],
            "consequence_warning": "We could not fully assess this content. Proceed with caution.",
            "safe_action_suggestion": "Verify this message by contacting the sender through a channel you trust.",
            "scam_pattern": None,
        }

    @staticmethod
    def _fallback_analysis(content: str, urls: list[str]) -> dict:
        """Fallback when no API key is configured (dev/test)."""
        return {
            "threat_level": "suspicious",
            "confidence_score": 50,
            "explanation": "Deep analysis unavailable. Based on available signals, we recommend caution.",
            "consequence_warning": "We could not fully assess this content. Proceeding could expose you to risk.",
            "safe_action_suggestion": "Verify this message by contacting the sender through a channel you trust.",
            "scam_pattern": None,
        }
