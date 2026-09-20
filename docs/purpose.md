# Purpose & Problem Statement

## Problem Statement

Traditional architecture diagramming tools present substantial friction to modern software engineering workflows:
1. **Opaque Binary Formats**: GUI diagramming tools store representations in proprietary binary or opaque JSON formats, making peer review, git diffing, and automated code review impractical.
2. **Heavy External C-Dependencies**: Existing Python diagram tools (such as Graphviz bindings or Cairo-based renderers) require system-level C-libraries (`graphviz`, `libcairo`, `pango`, `ImageMagick`). In automated CI/CD pipelines, containerized build environments, or restricted enterprise bastions, installing these external libraries introduces security vulnerabilities, compilation failures, and platform incompatibilities.
3. **Drift Between Code & Architecture**: Static image exports committed to documentation directories drift rapidly from the code they describe because there is no automated bridge between code changes, bills of materials (BOM), and diagram rendering.
4. **Rigid Layout & Canvas Collisions**: Simple diagram generators often suffer from coordinate stacking, text spilling out of icons/shapes, and unreadable routing that requires tedious manual coordinate tweaking.

---

## Architectural Motivation

`diagrams-as-code` was engineered from first principles to resolve these challenges:

- **100% Pure Python Standard Library**: The entire vector rendering engine, geometric calculations, constraint solver, orthogonal Manhattan router, and SVG generation require zero external runtime C-dependencies and zero third-party packages in Python 3.10+.
- **Living Documentation & BOM Generation**: Diagrams automatically yield structured Bill of Materials (BOM) in both Markdown table format and machine-readable JSON schemas, documenting component inventories, hardware specifications, protocols, and metadata alongside the visual graphic.
- **Fluent Pythonic Domain-Specific Language (DSL)**: Clean context-manager syntax (`with Diagram(...) as diag:`, `with diag.group(...) as g:`) with intuitive operator overloads (`shape_a >> diag.edge("Protocol") >> shape_b`).
- **Deterministic Geometric Solving**: Decouples shape instantiation from placement. Elements can be anchored absolutely, positioned relatively (`right_of`, `below`, `above`, `left_of`), or flow-arranged within hierarchically auto-bounding groups.
- **Production Visual Polish**: Built-in 13 dark, light, and accessibility themes with automatic contrast ratio calculation, 59 custom SVG vector icons, anti-spill multi-line text wrapping (`<tspan>`), and text-below-graphic layout options.

---

## Threat Model & Security Posture

### 1. Zero External Code Execution
The engine strictly parses Python DSL structures and outputs sanitized XML/SVG text. It executes no external shell processes, evaluates no untrusted dynamic code (`eval`, `exec`), and loads no dynamic shared C libraries during vector generation.

### 2. SVG XML Injection Prevention
All user-supplied strings (element identifiers, labels, metadata attributes, and protocol badge annotations) are rigorously escaped via `html.escape(..., quote=True)` before insertion into SVG XML text buffers. This guarantees protection against Cross-Site Scripting (XSS) or XML External Entity (XXE) attacks when SVG outputs are served in web browsers or embedded in HTML documentation.

### 3. File System Boundaries & Hermetic Execution
Local icon loading (`ShapeLibrary.load_icon_file` and `load_icons_from_directory`) restricts reads to specified SVG file paths and validates XML root elements before registration. All diagram generation runs hermetically within the designated repository or build container.

### 4. Supply Chain Security
With zero external runtime dependencies (`dependencies = []` in `pyproject.toml`), the attack surface from third-party supply chain compromise is minimized. Virtual environments, development packages, and test suites are strictly pinned and isolated via [`uv`](https://docs.astral.sh/uv/).
