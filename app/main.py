from fastapi import FastAPI, HTTPException
from fastapi.responses import Response
from prometheus_client import CONTENT_TYPE_LATEST, generate_latest

from app.config import get_settings
from app.integrations.oracle import OracleERPAdapter
from app.llm.evaluation import evaluate_answer
from app.llm.gateway import LLMGateway
from app.llm.providers import MockProvider
from app.llm.retrieval import LocalRetriever
from app.observability import telemetry_middleware
from app.schemas import (
    EnergyRecommendation,
    EnergyRequest,
    InvoiceRequest,
    LLMRequest,
    LLMResponse,
    RAGRequest,
    RAGResponse,
    WorkflowResult,
)
from app.services.energy import EnergyService
from app.services.workflows import InvoiceWorkflow

settings = get_settings()
providers = {"mock-oci": MockProvider("mock-oci"), "mock-openai": MockProvider("mock-openai")}
gateway = LLMGateway(
    providers,
    settings.llm_primary_provider,
    settings.llm_fallback_provider,
    settings.llm_request_budget_usd,
)
retriever = LocalRetriever()
energy_service = EnergyService()
invoice_workflow = InvoiceWorkflow(OracleERPAdapter())

app = FastAPI(
    title="Climate AI Operations Platform",
    version="1.0.0",
    description="ClimateTech backend, enterprise automation and internal LLM platform",
)
app.middleware("http")(telemetry_middleware)


@app.get("/health")
async def health() -> dict:
    return {"status": "healthy", "environment": settings.app_env, "providers": list(providers)}


@app.get("/metrics")
async def metrics() -> Response:
    return Response(generate_latest(), media_type=CONTENT_TYPE_LATEST)


@app.post("/v1/energy/recommendations", response_model=EnergyRecommendation)
async def energy_recommendation(req: EnergyRequest) -> EnergyRecommendation:
    return energy_service.recommend(req)


@app.post("/v1/workflows/invoices", response_model=WorkflowResult)
async def process_invoice(req: InvoiceRequest) -> WorkflowResult:
    return await invoice_workflow.execute(req)


@app.post("/v1/llm/generate", response_model=LLMResponse)
async def generate(req: LLMRequest) -> LLMResponse:
    try:
        return await gateway.generate(req.prompt, req.max_tokens, req.provider)
    except RuntimeError as exc:
        raise HTTPException(status_code=503, detail=str(exc)) from exc


@app.post("/v1/rag/ask", response_model=RAGResponse)
async def rag(req: RAGRequest) -> RAGResponse:
    chunks = retriever.search(req.question, req.top_k)
    context = "\n\n".join(f"[{chunk.source}] {chunk.text}" for chunk in chunks)
    prompt = (
        "Answer only from the supplied context and state uncertainty.\n"
        f"QUESTION: {req.question}\nCONTEXT:\n{context}"
    )
    llm = await gateway.generate(prompt)
    evaluation = evaluate_answer(
        req.question, llm.text, [chunk.text for chunk in chunks], llm.latency_ms
    )
    return RAGResponse(
        answer=llm.text,
        citations=list(dict.fromkeys(chunk.source for chunk in chunks)),
        evaluation=evaluation,
        request_id=llm.request_id,
    )
