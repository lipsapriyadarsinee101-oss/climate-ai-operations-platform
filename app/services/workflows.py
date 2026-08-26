from hashlib import sha256

from app.integrations.oracle import OracleERPAdapter
from app.schemas import InvoiceRequest, WorkflowResult


class InvoiceWorkflow:
    def __init__(self, erp: OracleERPAdapter):
        self.erp = erp
        self.completed: dict[str, WorkflowResult] = {}

    async def execute(self, invoice: InvoiceRequest) -> WorkflowResult:
        key = sha256(invoice.invoice_id.encode()).hexdigest()
        if key in self.completed:
            return self.completed[key]
        risk, reasons = 0.05, []
        if not invoice.purchase_order:
            risk += 0.45
            reasons.append("Missing purchase order")
        if invoice.amount_eur >= 10_000:
            risk += 0.4
            reasons.append("High-value invoice")
        if len(invoice.description.strip()) < 8:
            risk += 0.2
            reasons.append("Insufficient description")
        status = "auto_approved" if risk < 0.4 else "manual_review"
        erp_reference = (
            await self.erp.create_payable(invoice, key) if status == "auto_approved" else None
        )
        result = WorkflowResult(
            workflow_id=key[:16],
            status=status,
            risk_score=min(round(risk, 2), 1),
            reasons=reasons or ["Validation passed"],
            erp_reference=erp_reference,
        )
        self.completed[key] = result
        return result
