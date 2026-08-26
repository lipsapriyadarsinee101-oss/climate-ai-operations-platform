import asyncio
import time
from abc import ABC, abstractmethod
from dataclasses import dataclass


@dataclass
class ProviderResult:
    text: str
    input_tokens: int
    output_tokens: int
    latency_ms: float
    estimated_cost_usd: float


class LLMProvider(ABC):
    name: str

    @abstractmethod
    async def generate(self, prompt: str, max_tokens: int) -> ProviderResult: ...


class MockProvider(LLMProvider):
    def __init__(self, name: str, fail_on: str = "[FAIL]"):
        self.name = name
        self.fail_on = fail_on

    async def generate(self, prompt: str, max_tokens: int) -> ProviderResult:
        started = time.perf_counter()
        await asyncio.sleep(0.005)
        if self.fail_on in prompt:
            raise RuntimeError(f"Provider {self.name} unavailable")
        context = prompt.split("CONTEXT:", 1)[-1] if "CONTEXT:" in prompt else prompt
        text = (
            "Based on the supplied operational context: "
            + context[: min(600, max_tokens * 4)].strip()
        )
        input_tokens = max(1, len(prompt) // 4)
        output_tokens = max(1, len(text) // 4)
        return ProviderResult(
            text,
            input_tokens,
            output_tokens,
            (time.perf_counter() - started) * 1000,
            input_tokens * 0.0000003 + output_tokens * 0.0000006,
        )
