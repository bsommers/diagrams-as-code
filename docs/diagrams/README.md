# Visual Architecture Diagram Catalog

This directory contains visual models of the `diagrams-as-code` architecture rendered across three distinct formats for maximum interoperability:

| Format | File | Purpose & Tooling |
|---|---|---|
| **ASCII Text** | [`ascii_architecture.txt`](file:///home/bill/src/ai/diagrams-as-code/docs/diagrams/ascii_architecture.txt) | Terminal-friendly, zero-dependency schematic viewable in any shell (`cat`). |
| **Mermaid Flowchart** | [`architecture.mmd`](file:///home/bill/src/ai/diagrams-as-code/docs/diagrams/architecture.mmd) | High-level subsystem data flow and component hierarchy. |
| **Mermaid Sequence** | [`execution_lifecycle.mmd`](file:///home/bill/src/ai/diagrams-as-code/docs/diagrams/execution_lifecycle.mmd) | Context manager lifecycle, topological solving, and rendering sequence. |
| **Draw.io XML** | [`architecture.drawio`](file:///home/bill/src/ai/diagrams-as-code/docs/diagrams/architecture.drawio) | Native vector XML editable in [app.diagrams.net](https://app.diagrams.net) or VSCode Draw.io. |

---

## Viewing Instructions

- **Terminal:** `cat docs/diagrams/ascii_architecture.txt`
- **Mermaid:** View directly in GitHub Markdown preview, VSCode Mermaid extension, or [mermaid.live](https://mermaid.live).
- **Draw.io:** Open [`architecture.drawio`](file:///home/bill/src/ai/diagrams-as-code/docs/diagrams/architecture.drawio) in diagrams.net or Draw.io desktop.
