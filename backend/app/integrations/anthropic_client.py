import structlog

from app.core.config import get_settings

logger = structlog.get_logger()


class AnthropicClient:
    """Wrapper around the Anthropic API for LLM-based analysis."""

    def __init__(self):
        self._client = None

    async def _get_client(self):
        if self._client is None:
            import anthropic
            settings = get_settings()
            if not settings.anthropic_api_key:
                raise RuntimeError("Anthropic API key not configured")
            self._client = anthropic.AsyncAnthropic(api_key=settings.anthropic_api_key)
        return self._client

    async def analyze(
        self,
        system_prompt: str,
        user_message: str,
        model: str | None = None,
        max_tokens: int = 1024,
    ) -> str:
        settings = get_settings()
        model = model or settings.anthropic_model_fast

        try:
            client = await self._get_client()
            message = await client.messages.create(
                model=model,
                max_tokens=max_tokens,
                system=system_prompt,
                messages=[{"role": "user", "content": user_message}],
            )
            return message.content[0].text
        except Exception as exc:
            logger.error("anthropic_call_failed", error=str(exc), model=model)
            raise

    async def close(self):
        self._client = None
