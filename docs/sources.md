# Open-Source Libraries, Icons, and Specifications Provenance

This document details the origins, specifications, upstream repositories, and open-source licenses for all icons, standards, and software dependencies subsumed or utilized within `diagrams-as-code`.

---

## 1. Domain Vector Icon Catalog (`icons/` and `src/diagrams_as_code/shapes.py`)

The engine provides 60 handcrafted, resolution-independent vector icons across 8 domains (`cloud`, `ai`, `computer`, `datacenter`, `business_process`, `cybersecurity`, `network_engineering`, and `iiot`). All icons conform to a standard 24×24 pixel grid and are stroked at 2px in `currentColor` (`historian` and `vector_db` add a lighter interior accent stroke). The tree under `icons/` and its manifests are generated from `ShapeLibrary._ICON_CATALOG` by `tools/generate_icons.py`, so a file and the glyph the renderer draws are the same artwork. The glyph set is adapted from the following permissive open-source design systems:

| Icon Library / Source | Upstream Repository / Reference | License | Glyphs & Domains Derived |
| :--- | :--- | :--- | :--- |
| **[Lucide Icons](https://lucide.dev)** | [`lucide-icons/lucide`](https://github.com/lucide-icons/lucide) | [ISC License](https://github.com/lucide-icons/lucide/blob/main/LICENSE) | Foundational compute, device, and structural primitives: `server`, `terminal`, `laptop`, `mobile`, `cloud`, `database`, `user`, `document`, `message`, `lock`, `key`, `shield`. |
| **[Feather Icons](https://feathericons.com)** | [`feathericons/feather`](https://github.com/feathericons/feather) | [MIT License](https://github.com/feathericons/feather/blob/master/LICENSE) | Foundational 24×24 viewBox layout, 2px stroke width, and rounded geometric path styling conventions. |
| **[Tabler Icons](https://tabler.io/icons)** | [`tabler/tabler-icons`](https://github.com/tabler/tabler-icons) | [MIT License](https://github.com/tabler/tabler-icons/blob/master/LICENSE) | Infrastructure, hardware, and analytics glyphs: `brain`, `chip`, `vector_db`, `cooling`, `ups`, `cluster`, `vault`, `siem`, `soc`, `analytics`. |
| **[Cisco Network Topology Icons](https://www.cisco.com/c/en/us/about/brand-center/network-topology-icons.html)** | [Cisco Network Topology Stencils](https://www.cisco.com/c/en/us/about/brand-center/network-topology-icons.html) | Public Domain / Open Stencil Use | Network engineering symbols: `switch`, `router`, `core_router`, `bgp`, `mpls`, `firewall_ha`, `load_balancer`, `patch_panel`, `fiber_optic`. |
| **[CNCF Artwork](https://github.com/cncf/artwork)** | [`cncf/artwork`](https://github.com/cncf/artwork) | [CC-BY-4.0](https://creativecommons.org/licenses/by/4.0/) / [Apache-2.0](https://www.apache.org/licenses/LICENSE-2.0) | Cloud-native containerization and orchestration symbols: `kubernetes`, `container`, `cluster`. |
| **[AWS & Cloud Architecture Stencils](https://aws.amazon.com/architecture/icons/)** | [AWS Architecture Icons](https://aws.amazon.com/architecture/icons/) | Permissive Architectural Diagramming Use | Cloud network abstractions and boundary markers: `vpc`, `api_gateway`, `cdn`, `serverless`, `storage`, `dns`, `firewall`. |
| **[W3C Scalable Vector Graphics (SVG)](https://www.w3.org/TR/SVG2/)** | [W3C SVG 1.1 / 2.0 Recommendation](https://www.w3.org/TR/SVG2/) | [W3C Software and Document Notice](https://www.w3.org/Consortium/Legal/2015/copyright-software-and-document) | Vector path definitions, marker definitions (`marker-end`), drop shadow filters (`feDropShadow`), and `<tspan>` multiline text wrapping. |

All icon assets are cataloged in machine-readable manifests:
- YAML manifest: [`icons/icons.yaml`](../icons/icons.yaml)
- CSV manifest: [`icons/icons.csv`](../icons/icons.csv)

---

## 2. Software Dependencies & Build Tooling

The core engine is deliberately designed with zero runtime third-party dependencies. Development, testing, and packaging use the following tools:

| Component | Upstream Project | License | Category | Role in Repository |
| :--- | :--- | :--- | :--- | :--- |
| **Python Standard Library** | [python/cpython](https://github.com/python/cpython) | [PSF License](https://docs.python.org/3/license.html) | Core Runtime | **Zero-dependency runtime**: XML parsing and generation (`xml.etree.ElementTree`), data modeling (`dataclasses`, `enum`), geometric math (`math`), typing contracts (`typing`), file paths (`pathlib`), regular expressions (`re`). |
| **Astral `uv`** | [astral-sh/uv](https://github.com/astral-sh/uv) | [Apache-2.0](https://github.com/astral-sh/uv/blob/main/LICENSE-APACHE) / [MIT](https://github.com/astral-sh/uv/blob/main/LICENSE-MIT) | Tooling & Packaging | High-performance virtual environment provisioning, lockfile resolution (`uv.lock`), and script/test execution runner. |
| **Hatchling** | [pypa/hatch](https://github.com/pypa/hatch) | [MIT License](https://github.com/pypa/hatch/blob/master/LICENSE.txt) | Build Backend | Standard PEP 517/621 wheel packaging backend configured in `pyproject.toml`. |
| **pytest** | [pytest-dev/pytest](https://github.com/pytest-dev/pytest) | [MIT License](https://github.com/pytest-dev/pytest/blob/main/LICENSE) | Dev / Test Runner | Test execution suite covering unit, integration, and end-to-end diagram verification in `tests/`. |
| **resvg-py** | [baseplate-admin/resvg-py](https://github.com/baseplate-admin/resvg-py) | [MIT License](https://github.com/baseplate-admin/resvg-py/blob/master/LICENSE) | Optional Runtime | Headless, Rust-based SVG-to-PNG rasterizer. Imported at runtime by `Diagram.render_png()` (`src/diagrams_as_code/diagram.py`) as the first of four PNG backends; not required for SVG output, which stays pure standard library. Installed as a dev dependency via `uv add --dev resvg-py`. |
