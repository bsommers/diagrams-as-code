# Diagrams-as-Code: Documentation Hub

Welcome to the comprehensive documentation suite for `diagrams-as-code`. This hub provides architectural blueprints, operational runbooks, step-by-step recipes, and multi-format visual diagrams.

---

## Documentation Index

| Document | Topic & Focus |
|---|---|
| [**Purpose & Threat Model**](file:///home/bill/src/ai/diagrams-as-code/docs/purpose.md) | Problem statement, architectural motivation, pure standard library philosophy, and security threat model. |
| [**System Architecture**](file:///home/bill/src/ai/diagrams-as-code/docs/architecture.md) | Technical specifications: geometry engine, topological constraint solver, orthogonal router, SVG renderer, and living BOM pipeline. |
| [**Running & Installation Guide**](file:///home/bill/src/ai/diagrams-as-code/docs/running.md) | Prerequisites, virtual environment provisioning with `uv`, CLI commands, test execution, and Docker setup. |
| [**How-To Recipes & Troubleshooting**](file:///home/bill/src/ai/diagrams-as-code/docs/how-to.md) | Step-by-step recipes for custom themes, text layout optimization, standalone vector icons, living documentation, and troubleshooting matrix. |
| [**Visual Architecture Diagrams**](file:///home/bill/src/ai/diagrams-as-code/docs/diagrams/README.md) | Visual model catalog containing terminal ASCII text, standalone Mermaid flowcharts, Mermaid sequence lifecycles, and native draw.io XML. |
| [**Layout Root Cause Post-Mortem**](file:///home/bill/src/ai/diagrams-as-code/docs/LAYOUT_ROOT_CAUSE.md) | Diagnostic analysis and resolution of context-manager lifecycle coordinate resolution and negative bounding box clipping. |
| [**Changelog & Version History**](file:///home/bill/src/ai/diagrams-as-code/docs/CHANGELOG.md) | Release notes, version history, feature additions, and bug fixes across all versions. |

---

## Visual Architecture Quick Preview

```
┌────────────────────────────────────────────────────────────────────────┐
│                        User Architecture Script                        │
│                with Diagram("Title", theme="nord") as diag:            │
└───────────────────────────────────┬────────────────────────────────────┘
                                    │
                                    ▼
┌────────────────────────────────────────────────────────────────────────┐
│                    Declarative Object Model & Stack                    │
│                 Diagram  │  Shapes  │  Groups  │  Edges                │
└───────────────────────────────────┬────────────────────────────────────┘
                                    │
                                    ▼
┌────────────────────────────────────────────────────────────────────────┐
│               Topological Constraint Solver & Auto-Framing             │
│            Relative Alignments  │  DAG Resolution  │  Groups           │
└───────────────────────────────────┬────────────────────────────────────┘
                                    │
                                    ▼
┌────────────────────────────────────────────────────────────────────────┐
│                   Orthogonal Manhattan Router (A*)                     │
│               Cardinal Ports  │  Obstacles  │  Badges                  │
└───────────────────────────────────┬────────────────────────────────────┘
                                    │
                   ┌────────────────┴────────────────┐
                   ▼                                 ▼
┌─────────────────────────────────────┐ ┌────────────────────────────────┐
│             SVGRenderer             │ │          BOMGenerator          │
│  - 13 Themes (Light/Dark/A11y)      │ │  - Markdown Tables             │
│  - 59 Built-in Vector Icons         │ │  - Machine-Readable JSON       │
│  - Multi-line <tspan> Wrap          │ └────────────────────────────────┘
│  - Text-Below-Graphic Tiles         │
└──────────────────┬──────────────────┘
                   │
                   ▼
┌─────────────────────────────────────┐
│         resvg-py Rasterizer         │
│  - High-Resolution Crisp PNG Images │
└─────────────────────────────────────┘
```

For higher resolution ASCII schematics, view [`docs/diagrams/ascii_architecture.txt`](file:///home/bill/src/ai/diagrams-as-code/docs/diagrams/ascii_architecture.txt).
