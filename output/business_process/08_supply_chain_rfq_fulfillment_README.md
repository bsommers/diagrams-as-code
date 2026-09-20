# Global Supply Chain RFQ & Sourcing

![Architecture Diagram](./08_supply_chain_rfq_fulfillment.svg)

## Bill of Materials

| Symbol / ID | Label | Kind | Group | Technical Notes / Metadata |
| :--- | :--- | :--- | :--- | :--- |
| `demand_plan` | **Material Demand Forecast** | box | Supply Planning | horizon: Quarterly Plan |
| `rfq_portal` | **Global Supplier RFQ Portal** | box | Procurement | suppliers: Global Tier 1 Vendors |
| `bid_eval` | **Multi-Criteria Bid Scoring** | box | Procurement | criteria: Price, Quality, Lead Time |
| `freight` | **Ocean & Air Freight Booking** | box | Logistics Operations | incoterms: FOB Port of Origin |
| `customs` | **Customs Broker Clearance** | box | Logistics Operations | tariff: Harmonized Code Verified |
| `dc_intake` | **Central Distribution Center** | box | Warehouse Fulfillment | pallet: Automated AS/RS Intake |

## Connections

| Source | Target | Protocol / Label | Style | Routing |
| :--- | :--- | :--- | :--- | :--- |
| **Material Demand Forecast** (`demand_plan`) | **Global Supplier RFQ Portal** (`rfq_portal`) | Trigger Requisition | solid | orthogonal |
| **Global Supplier RFQ Portal** (`rfq_portal`) | **Multi-Criteria Bid Scoring** (`bid_eval`) | Compile Bids | solid | orthogonal |
| **Multi-Criteria Bid Scoring** (`bid_eval`) | **Ocean & Air Freight Booking** (`freight`) | Award Contract & Ship | solid | orthogonal |
| **Ocean & Air Freight Booking** (`freight`) | **Customs Broker Clearance** (`customs`) | Present Bill of Lading | solid | orthogonal |
| **Customs Broker Clearance** (`customs`) | **Central Distribution Center** (`dc_intake`) | Release Cargo to Racks | solid | orthogonal |
