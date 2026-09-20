# ITSM Enterprise Change Advisory Board (CAB)

![Architecture Diagram](./10_enterprise_change_management.svg)

## Bill of Materials

| Symbol / ID | Label | Kind | Group | Technical Notes / Metadata |
| :--- | :--- | :--- | :--- | :--- |
| `engineer` | **Systems Engineer** | box | RFC Initiation | role: Cloud Platform Lead |
| `rfc_doc` | **Request for Change (RFC)** | box | RFC Initiation | type: Critical Kernel Patch |
| `risk_calc` | **Risk & Impact Matrix** | box | Governance Gates | score: Severity High / Low Risk |
| `cab_board` | **Change Advisory Board (CAB)** | box | Governance Gates | quorum: Security, Network, Product Leads |
| `maint_window` | **Maintenance Window Execution** | box | Execution Phase | schedule: Sunday 02:00 UTC |
| `health_verify` | **Automated Post-Change Health Check** | box | Verification | test: Synthetic Smoke Tests |
| `rollback` | **Automated Rollback Safeguard** | box | Verification | trigger: P99 Latency Regression |

## Connections

| Source | Target | Protocol / Label | Style | Routing |
| :--- | :--- | :--- | :--- | :--- |
| **Systems Engineer** (`engineer`) | **Request for Change (RFC)** (`rfc_doc`) | Draft RFC Proposal | solid | orthogonal |
| **Request for Change (RFC)** (`rfc_doc`) | **Risk & Impact Matrix** (`risk_calc`) | Calculate Impact Score | solid | orthogonal |
| **Risk & Impact Matrix** (`risk_calc`) | **Change Advisory Board (CAB)** (`cab_board`) | Present to CAB Review | solid | orthogonal |
| **Change Advisory Board (CAB)** (`cab_board`) | **Maintenance Window Execution** (`maint_window`) | Approve Execution Window | solid | orthogonal |
| **Maintenance Window Execution** (`maint_window`) | **Automated Post-Change Health Check** (`health_verify`) | Run Post-Change Verification | solid | orthogonal |
| **Automated Post-Change Health Check** (`health_verify`) | **Automated Rollback Safeguard** (`rollback`) | Abnormal Signals Detected | dashed | orthogonal |
