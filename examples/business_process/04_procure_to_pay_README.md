# Procure-to-Pay (P2P) Sourcing Process

![Architecture Diagram](./04_procure_to_pay.svg)

## Bill of Materials

| Symbol / ID | Label | Kind | Group | Technical Notes / Metadata |
| :--- | :--- | :--- | :--- | :--- |
| `requester` | **Internal Department Lead** | box | Requisition | dept: Engineering |
| `req_approval` | **Manager Spend Approval** | box | Approval Gates | threshold: Under $50k Budget |
| `po_dispatch` | **ERP Purchase Order (PO)** | box | Procurement | system: SAP S/4HANA |
| `vendor` | **Approved Enterprise Vendor** | box | Vendor Domain | terms: Net 45 |
| `match_3way` | **3-Way Match Verification** | box | Accounting | match: PO vs Receipt vs Invoice |
| `ap_disburse` | **Accounts Payable Payment** | box | Accounting | method: Automated ACH Transfer |

## Connections

| Source | Target | Protocol / Label | Style | Routing |
| :--- | :--- | :--- | :--- | :--- |
| **Internal Department Lead** (`requester`) | **Manager Spend Approval** (`req_approval`) | Submit Requisition | solid | orthogonal |
| **Manager Spend Approval** (`req_approval`) | **ERP Purchase Order (PO)** (`po_dispatch`) | Authorize Spend | solid | orthogonal |
| **ERP Purchase Order (PO)** (`po_dispatch`) | **Approved Enterprise Vendor** (`vendor`) | Transmit PO | solid | orthogonal |
| **Approved Enterprise Vendor** (`vendor`) | **3-Way Match Verification** (`match_3way`) | Deliver Goods & Invoice | solid | orthogonal |
| **3-Way Match Verification** (`match_3way`) | **Accounts Payable Payment** (`ap_disburse`) | Approve Payment | solid | orthogonal |
