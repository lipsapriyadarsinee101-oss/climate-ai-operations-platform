from dataclasses import dataclass
from hashlib import sha256

from app.schemas import InvoiceRequest


@dataclass
class OracleERPAdapter:
    """Local adapter matching the boundary of a future Oracle ERP/OIC client."""

    async def create_payable(self, invoice: InvoiceRequest, idempotency_key: str) -> str:
        digest = sha256(f"{invoice.invoice_id}:{idempotency_key}".encode()).hexdigest()[:12]
        return f"ORACLE-AP-{digest.upper()}"
