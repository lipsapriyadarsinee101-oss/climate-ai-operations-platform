from typing import Literal

from pydantic import BaseModel, Field


class EnergyRequest(BaseModel):
    household_id: str
    monthly_kwh: list[float] = Field(min_length=12, max_length=12)
    solar_capacity_kw: float = Field(ge=0, le=30)
    tariff_eur_kwh: float = Field(gt=0, le=2)


class EnergyRecommendation(BaseModel):
    annual_kwh: float
    estimated_cost_eur: float
    estimated_solar_coverage_pct: float
    annual_savings_eur: float
    actions: list[str]


class InvoiceRequest(BaseModel):
    invoice_id: str
    supplier: str
    amount_eur: float = Field(gt=0)
    purchase_order: str | None = None
    description: str


class WorkflowResult(BaseModel):
    workflow_id: str
    status: Literal["auto_approved", "manual_review", "rejected"]
    risk_score: float
    reasons: list[str]
    erp_reference: str | None = None


class LLMRequest(BaseModel):
    prompt: str = Field(min_length=1, max_length=12000)
    provider: str | None = None
    max_tokens: int = Field(default=500, ge=1, le=4000)


class LLMResponse(BaseModel):
    text: str
    provider: str
    input_tokens: int
    output_tokens: int
    latency_ms: float
    estimated_cost_usd: float
    request_id: str


class RAGRequest(BaseModel):
    question: str
    top_k: int = Field(default=3, ge=1, le=8)


class RAGResponse(BaseModel):
    answer: str
    citations: list[str]
    evaluation: dict[str, float]
    request_id: str
