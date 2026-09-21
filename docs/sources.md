# Open-Source Libraries, Icons, and Specifications Provenance

This document records the origin and license of everything `diagrams-as-code` ships or invokes: the icons it draws, the specifications it implements, the tools it is built and tested with, and the contents of its container image. Where a component is original work of this project, it says so; where it is third-party, it names the real license.

---

## 1. Domain Vector Icon Catalog (`icons/` and `src/diagrams_as_code/shapes.py`)

The engine provides 60 handcrafted, resolution-independent vector icons across 8 domains (`cloud`, `ai`, `computer`, `datacenter`, `business_process`, `cybersecurity`, `network_engineering`, and `iiot`). All icons conform to a standard 24x24 pixel grid and are stroked at 2px in `currentColor` (`historian` and `vector_db` add a lighter interior accent stroke). The tree under `icons/` and its manifests are generated from `ShapeLibrary._ICON_CATALOG` by `tools/generate_icons.py`, so a file and the glyph the renderer draws are the same artwork.

### Authorship

**Every glyph is original geometry written for this project**, covered by this repository's [MIT license](../LICENSE). No third-party icon set is vendored, traced, or redistributed here, and no upstream icon license obligations attach to this repository.

The artwork is not exported from a design tool. Each glyph is emitted as SVG primitives — `line`, `circle`, `rect`, `path`, `polyline`, `ellipse`, `polygon` — by `ShapeLibrary._render_icon_content` in [`src/diagrams_as_code/shapes.py`](../src/diagrams_as_code/shapes.py), placed on whole-number coordinates of the 24x24 grid. [`icons/datacenter/kubernetes.svg`](../icons/datacenter/kubernetes.svg), for instance, is a circle with eight straight spokes; it neither derives from nor resembles the seven-sided CNCF helm.

### Visual conventions (not sources)

The catalog follows the conventions shared by modern open-source icon sets: a 24x24 viewBox, a uniform stroke weight, and `currentColor` inheritance so an icon takes its color from the embedding document. That idiom was popularized by [Feather](https://feathericons.com) and is shared by [Lucide](https://lucide.dev) and [Tabler](https://tabler.io/icons).

**A convention is not artwork.** Nothing is copied from those projects, none of their licenses applies to this repository, and no attribution to them is owed or claimed. They are named here only so a reader who likes the style knows where the idiom comes from.

### Vendor and product names

`ShapeLibrary` accepts aliases such as `grafana`, `kafka`, `s3`, and `docker`. These are naming conveniences that resolve to generic glyphs; see the alias table in [`icons/README.md`](../icons/README.md). **No vendor logo, wordmark, or trademarked symbol is reproduced anywhere in this repository**, and all product names remain the property of their respective owners.

If you want a vendor's own symbol set in your diagrams, obtain it from the vendor and read their terms directly — for example [Cisco's network topology icons](https://www.cisco.com/c/en/us/about/brand-center/network-topology-icons.html) or the [AWS Architecture Icons](https://aws.amazon.com/architecture/icons/) terms of use. Both are conditional brand-asset programs, not open-source licenses. This project neither bundles nor relicenses them.

### Specifications implemented

| Specification | Reference | License / Notice | Used for |
| :--- | :--- | :--- | :--- |
| **W3C Scalable Vector Graphics (SVG)** | [SVG 1.1 / 2.0 Recommendation](https://www.w3.org/TR/SVG2/) | [W3C Software and Document Notice](https://www.w3.org/Consortium/Legal/2015/copyright-software-and-document) | Vector path definitions, marker definitions (`marker-end`), drop-shadow filters (`feDropShadow`), and `<tspan>` multi-line text wrapping. |

### Machine-readable manifests

Every icon is cataloged in both manifests, which are generated alongside the tree:
- YAML manifest: [`icons/icons.yaml`](../icons/icons.yaml)
- CSV manifest: [`icons/icons.csv`](../icons/icons.csv)

> **Correction (2026-09-21).** Revisions of this document before commit `826c227` credited these icons to Lucide, Feather, Tabler, Cisco, CNCF, and AWS with per-glyph derivation claims, and named two licenses that do not exist ("Public Domain / Open Stencil Use" and "Permissive Architectural Diagramming Use"). The glyphs were original work throughout; the attribution was incorrect and is retracted here.


---

## 2. Software Dependencies & Build Tooling

The core engine is deliberately designed with zero runtime third-party dependencies: `render_svg()` and the BOM generator use only the standard library. Development, testing, packaging, and the optional PNG rasterization path use the components below.

The licenses here are **not uniformly permissive** — the second and third PNG backends (CairoSVG, Inkscape) are copyleft — so each component is listed with its own license and with how this project uses it: imported into the process, or located on `PATH` and invoked as an external binary.

| Component | Upstream Project | License | Category | Role in Repository |
| :--- | :--- | :--- | :--- | :--- |
| **Python Standard Library** | [python/cpython](https://github.com/python/cpython) | [PSF License](https://docs.python.org/3/license.html) | Core Runtime | **Zero-dependency runtime**: XML parsing and generation (`xml.etree.ElementTree`), data modeling (`dataclasses`, `enum`), geometric math (`math`), typing contracts (`typing`), file paths (`pathlib`), regular expressions (`re`). |
| **Astral `uv`** | [astral-sh/uv](https://github.com/astral-sh/uv) | [Apache-2.0](https://github.com/astral-sh/uv/blob/main/LICENSE-APACHE) / [MIT](https://github.com/astral-sh/uv/blob/main/LICENSE-MIT) | Tooling & Packaging | High-performance virtual environment provisioning, lockfile resolution (`uv.lock`), and script/test execution runner. |
| **Hatchling** | [pypa/hatch](https://github.com/pypa/hatch) | [MIT License](https://github.com/pypa/hatch/blob/master/LICENSE.txt) | Build Backend | Standard PEP 517/621 wheel packaging backend configured in `pyproject.toml`. |
| **pytest** | [pytest-dev/pytest](https://github.com/pytest-dev/pytest) | [MIT License](https://github.com/pytest-dev/pytest/blob/main/LICENSE) | Dev / Test Runner | Test execution suite covering unit, integration, and end-to-end diagram verification in `tests/`. |
| **resvg-py** | [baseplate-admin/resvg-py](https://github.com/baseplate-admin/resvg-py) | [MIT License](https://github.com/baseplate-admin/resvg-py/blob/master/LICENSE) | Optional Runtime | Headless, Rust-based SVG-to-PNG rasterizer. Imported at runtime by `Diagram.render_png()` (`src/diagrams_as_code/diagram.py`) as the first of four PNG backends; not required for SVG output, which stays pure standard library. Installed as a dev dependency via `uv add --dev resvg-py`. |
| **CairoSVG** | [Kozea/CairoSVG](https://github.com/Kozea/CairoSVG) | [LGPL-3.0-or-later](https://github.com/Kozea/CairoSVG/blob/main/LICENSE) | Optional Runtime (fallback, **copyleft**) | Second PNG backend tried by `Diagram.render_png()`. Not declared in `pyproject.toml` and never installed by `uv sync`; used only when it already exists in the caller's environment. It binds the Cairo C library, so it falls outside the zero-C-dependency guarantee, which covers SVG output only. |
| **Inkscape** | [inkscape/inkscape](https://gitlab.com/inkscape/inkscape) | [GPL-3.0-or-later](https://gitlab.com/inkscape/inkscape/-/blob/master/COPYING) | Optional Runtime (external binary, **copyleft**) | Third PNG backend. Located with `shutil.which("inkscape")` and run as a subprocess (`inkscape <svg> -o <png>`); never imported, linked against, or redistributed by this project. |
| **ImageMagick** | [ImageMagick/ImageMagick](https://github.com/ImageMagick/ImageMagick) | [ImageMagick License](https://imagemagick.org/script/license.php) (Apache-2.0 derived) | Optional Runtime (external binary) | Fourth and final PNG backend. Located with `shutil.which("magick")` or `shutil.which("convert")` and run as a subprocess. When none of the four backends is present, `render_png()` raises `RuntimeError`; SVG output is unaffected. |

The four PNG backends are tried in the order listed (`resvg-py` → CairoSVG → Inkscape → ImageMagick) by `Diagram.render_png()` in [`src/diagrams_as_code/diagram.py`](../src/diagrams_as_code/diagram.py). Only the first is installed by this repository's dev dependency group; the rest are used opportunistically if the host already provides them.

---

## 3. Container Image Contents (`Dockerfile`)

`docker build` produces the only artifact of this project that redistributes third-party binaries. The Python package itself ships no compiled code and no font outlines.

| Component | Upstream Project | License | Role in Image |
| :--- | :--- | :--- | :--- |
| **`ghcr.io/astral-sh/uv:python3.12-bookworm-slim`** | [astral-sh/uv](https://github.com/astral-sh/uv) | [Apache-2.0](https://github.com/astral-sh/uv/blob/main/LICENSE-APACHE) / [MIT](https://github.com/astral-sh/uv/blob/main/LICENSE-MIT) (the `uv` binary) over the Debian base below | Base image declared at [`Dockerfile`](../Dockerfile) line 2. Supplies CPython 3.12 ([PSF License](https://docs.python.org/3/license.html)) and the `uv` binary. |
| **Debian 12 "bookworm" (slim)** | [Debian](https://www.debian.org/) | Per-package; see [Debian Free Software Guidelines](https://www.debian.org/social_contract#guidelines) and each package's `/usr/share/doc/<pkg>/copyright` inside the image | Operating-system layer underneath the base image: shell, libc, CA certificates, and the `apt` toolchain used during build. |
| **`fonts-dejavu-core`** | [dejavu-fonts/dejavu-fonts](https://github.com/dejavu-fonts/dejavu-fonts) | [DejaVu Fonts License](https://dejavu-fonts.github.io/License.html) (Bitstream Vera derivative, permissive) | Installed via `apt-get` in the `Dockerfile` so a rasterizer running inside the container resolves a real `sans-serif` face. Diagram SVGs name font families (`Inter, -apple-system, …, sans-serif`) and embed no outlines, so nothing from this package is copied into generated output. |

This table covers what the project itself selects and adds. For a complete per-package inventory of the Debian layer, generate an SBOM from the built image (`docker sbom iiot-diagrams:latest` or `syft iiot-diagrams:latest`).
