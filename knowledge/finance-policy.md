# Finance Automation Policy

Invoices below EUR 10,000 may be automatically approved when they contain a valid purchase order, a recognized supplier, and a meaningful description. Duplicate invoice identifiers must return the original result and must never create a second payable.

Invoices of EUR 10,000 or more require manual approval. Invoices without a purchase order require manual review regardless of value. Every automated decision must retain its validation reasons, workflow identifier, and ERP reference.

