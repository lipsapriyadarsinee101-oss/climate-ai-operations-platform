import uuid

from app.llm.providers import LLMProvider
from app.observability import LLM_CALLS, LLM_COST
from app.schemas import LLMResponse


class LLMGateway:
    def __init__(
        self,
        providers: dict[str, LLMProvider],
        primary: str,
        fallback: str,
        request_budget_usd: float,
    ):
        self.providers, self.primary, self.fallback, self.request_budget_usd = (
            providers,
            primary,
            fallback,
            request_budget_usd,
        )

    async def generate(
        self, prompt: str, max_tokens: int = 500, provider: str | None = None
    ) -> LLMResponse:
        request_id = str(uuid.uuid4())
        candidates = [provider] if provider else [self.primary, self.fallback]
        last_error: Exception | None = None
        for name in dict.fromkeys(candidates):
            if name not in self.providers:
                continue
            try:
                result = await self.providers[name].generate(prompt, max_tokens)
                if result.estimated_cost_usd > self.request_budget_usd:
                    raise ValueError("Request exceeds configured LLM budget")
                LLM_CALLS.labels(name, "success").inc()
                LLM_COST.labels(name).inc(result.estimated_cost_usd)
                return LLMResponse(provider=name, request_id=request_id, **result.__dict__)
            except Exception as exc:
                last_error = exc
                LLM_CALLS.labels(name, "failure").inc()
        raise RuntimeError(f"All LLM providers failed: {last_error}")
