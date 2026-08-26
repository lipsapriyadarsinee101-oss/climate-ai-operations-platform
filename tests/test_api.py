from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)


def test_health():
    assert client.get("/health").json()["status"] == "healthy"


def test_energy_recommendation():
    payload = {
        "household_id": "HH-1",
        "monthly_kwh": [400] * 12,
        "solar_capacity_kw": 4,
        "tariff_eur_kwh": 0.32,
    }
    result = client.post("/v1/energy/recommendations", json=payload)
    assert result.status_code == 200
    assert result.json()["annual_kwh"] == 4800
    assert result.json()["annual_savings_eur"] > 0


def test_invoice_is_idempotent():
    payload = {
        "invoice_id": "INV-1",
        "supplier": "Heat GmbH",
        "amount_eur": 2500,
        "purchase_order": "PO-1",
        "description": "Heat pump service",
    }
    first = client.post("/v1/workflows/invoices", json=payload).json()
    second = client.post("/v1/workflows/invoices", json=payload).json()
    assert first == second
    assert first["status"] == "auto_approved"


def test_high_value_invoice_requires_review():
    payload = {
        "invoice_id": "INV-2",
        "supplier": "Solar GmbH",
        "amount_eur": 12000,
        "purchase_order": "PO-2",
        "description": "Solar installation",
    }
    result = client.post("/v1/workflows/invoices", json=payload).json()
    assert result["status"] == "manual_review"
    assert result["erp_reference"] is None


def test_rag_returns_citations_and_evaluation():
    result = client.post(
        "/v1/rag/ask", json={"question": "When is manual invoice approval required?"}
    )
    assert result.status_code == 200
    assert "finance-policy.md" in result.json()["citations"]
    assert "groundedness" in result.json()["evaluation"]
