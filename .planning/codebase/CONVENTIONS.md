---
last_mapped_commit: aa12f844a5d25922af7be204ce6e5ef29d89db57
---

# Coding Conventions

**Analysis Date:** 2026-09-19

## Naming Patterns

**Files:**
- Script definitions: Mixed kebab-case and snake_case (`diagram-architecture-slide.py`, `iiot_theme.py`, `themed_main.py`)
- Test scripts: Prefixed with `test_` (`test_bom.py`, `test_docs_bom.py`)

**Classes:**
- PascalCase for all classes (`IIoTPalette`)

**Functions & Methods:**
- snake_case for all methods (`get_node`, `load_icons`, `generate_readme`, `push_to_github`, `upload_to_s3`)
- Private helper methods prefixed with single underscore (`_bootstrap`)

**Variables & Constants:**
- Configuration constants in UPPER_SNAKE_CASE (`IIOT_YELLOW = "#FFC000"`, `IIOT_BLACK = "#000000"`, `GLOBAL_ATTR`, `BASE_NODE_ATTR`)
- Local variables in snake_case (`node_info`, `used_symbols`, `diag_name`, `img_file`)

## Code Style

**Formatting:**
- 4-space indentation following standard PEP 8 conventions
- Double quotes primarily used for diagram labels and dictionary keys
- Diagram DSL chain syntax:
  - Directed edge connection: `source >> Edge(...) >> target`
  - Group/Cluster scoping via context managers: `with Cluster("Name", graph_attr={...}):`
  - Node list bulk connections: `sensors >> Edge(...) >> [node1, node2]`

**Error Handling:**
- Defensive fallback handling for icon lookups:
  ```python
  node_info = self.icon_data.get(sym_key, {"path": "./icons/default.png", "notes": "Unknown"})
  ```
- Catch-all exception handling around Git and AWS operations with stdout warning messages:
  ```python
  except Exception as e:
      print(f"Git Error: {e}")
  ```

**Branding & Styling:**
- Standard corporate palette constants defined at the top of diagram scripts:
  - Background: Black (`#000000`) or Dark Grey (`#1A1A1A`)
  - Accent / Lines: Gold / Yellow (`#FFC000` or `#F3B01C`)
  - Node text / titles: Black text on gold fill, or gold text on dark background
