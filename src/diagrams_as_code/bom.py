"""Bill of Materials (BOM) & Living Documentation Generator."""
from __future__ import annotations

import json
from pathlib import Path
from typing import TYPE_CHECKING, Any, Optional, Sequence, Union

if TYPE_CHECKING:
    from diagrams_as_code.diagram import Diagram


def _escape_cell(val: Any) -> str:
    """Format and escape text for Markdown table cells."""
    if val is None:
        return "-"
    s = str(val).replace("\r\n", " ").replace("\n", " ").replace("\r", " ")
    return s.replace("|", r"\|").strip()


class BOMGenerator:
    """Extracts component inventory, connections, and generates living documentation."""

    def __init__(self, diagram: Union[Diagram, Any]) -> None:
        self.diagram = diagram

    def items(self) -> list[dict[str, Any]]:
        """Extract inventory of all shapes, kinds, parent groups, and metadata."""
        result: list[dict[str, Any]] = []
        for s in getattr(self.diagram, "shapes", []):
            group_label: Optional[str] = None
            if getattr(s, "parent", None) is not None:
                parent = s.parent
                group_label = getattr(parent, "label", getattr(parent, "id", None))

            result.append(
                {
                    "id": s.id,
                    "label": s.label,
                    "kind": getattr(s, "kind", "box"),
                    "group": group_label,
                    "metadata": dict(s.metadata)
                    if getattr(s, "metadata", None)
                    else {},
                }
            )
        return result

    def connections(self) -> list[dict[str, Any]]:
        """Extract edge connections, endpoints, protocol labels, ports, and styles."""
        result: list[dict[str, Any]] = []
        for e in getattr(self.diagram, "edges", []):
            source_id = getattr(e.source, "id", str(e.source))
            source_label = getattr(e.source, "label", None) or source_id
            target_id = getattr(e.target, "id", str(e.target))
            target_label = getattr(e.target, "label", None) or target_id

            routing_val = (
                e.routing.value if hasattr(e.routing, "value") else str(e.routing)
            )
            source_port_val = (
                e.source_port.value
                if hasattr(e.source_port, "value")
                else (str(e.source_port) if e.source_port else None)
            )
            target_port_val = (
                e.target_port.value
                if hasattr(e.target_port, "value")
                else (str(e.target_port) if e.target_port else None)
            )

            result.append(
                {
                    "source": source_id,
                    "source_label": source_label,
                    "target": target_id,
                    "target_label": target_label,
                    "protocol": e.label,
                    "label": e.label,
                    "style": getattr(e, "style", "solid"),
                    "color": getattr(e, "color", None),
                    "routing": routing_val,
                    "source_port": source_port_val,
                    "target_port": target_port_val,
                    "arrow_head": getattr(e, "arrow_head", True),
                    "arrow_tail": getattr(e, "arrow_tail", False),
                    "metadata": dict(e.metadata)
                    if getattr(e, "metadata", None)
                    else {},
                }
            )
        return result

    def to_dict(self) -> dict[str, Any]:
        """Produce structured dictionary representation of the BOM."""
        items_data = self.items()
        conns_data = self.connections()
        groups_data = []
        for g in getattr(self.diagram, "groups", []):
            groups_data.append(
                {
                    "id": g.id,
                    "label": g.label,
                    "children": [
                        getattr(c, "id", str(c))
                        for c in getattr(g, "children", [])
                    ],
                    "metadata": dict(g.metadata)
                    if getattr(g, "metadata", None)
                    else {},
                }
            )

        return {
            "title": getattr(self.diagram, "title", "IIoT Architecture"),
            "total_components": len(items_data),
            "total_connections": len(conns_data),
            "items": items_data,
            "connections": conns_data,
            "groups": groups_data,
        }

    def to_json(self, indent: int = 2) -> str:
        """Serialize diagram inventory to formatted JSON string."""
        return json.dumps(self.to_dict(), indent=indent, default=str)

    def to_markdown(
        self,
        title: str = "Bill of Materials",
        image_file: Optional[str] = None,
        columns: Optional[Sequence[str]] = None,
    ) -> str:
        """Produce Markdown table of diagram components and optional image link."""
        col_list = (
            list(columns)
            if columns is not None
            else [
                "Symbol / ID",
                "Label",
                "Kind",
                "Group",
                "Technical Notes / Metadata",
            ]
        )

        lines: list[str] = []
        if image_file:
            img_src = (
                image_file
                if (
                    image_file.startswith(".")
                    or image_file.startswith("/")
                    or "://" in image_file
                )
                else f"./{image_file}"
            )
            lines.append(f"![Architecture Diagram]({img_src})")
            lines.append("")

        if title:
            lines.append(f"## {title}")
            lines.append("")

        header_str = "| " + " | ".join(col_list) + " |"
        sep_str = "| " + " | ".join([":---"] * len(col_list)) + " |"
        lines.append(header_str)
        lines.append(sep_str)

        for it in self.items():
            row_cells: list[str] = []
            for col in col_list:
                col_lower = col.lower().strip()
                if "symbol" in col_lower or col_lower == "id":
                    row_cells.append(f"`{_escape_cell(it['id'])}`")
                elif col_lower == "label":
                    row_cells.append(f"**{_escape_cell(it['label'])}**")
                elif col_lower == "kind":
                    row_cells.append(_escape_cell(it["kind"]))
                elif col_lower == "group":
                    row_cells.append(
                        _escape_cell(it["group"]) if it.get("group") else "-"
                    )
                elif "metadata" in col_lower or "note" in col_lower:
                    if it["metadata"]:
                        parts = [
                            f"{_escape_cell(k)}: {_escape_cell(v)}"
                            for k, v in it["metadata"].items()
                        ]
                        row_cells.append(", ".join(parts))
                    else:
                        row_cells.append("-")
                else:
                    val = it.get(col, it.get(col_lower, "-"))
                    row_cells.append(_escape_cell(val) if val else "-")
            lines.append("| " + " | ".join(row_cells) + " |")

        return "\n".join(lines)

    def connections_to_markdown(self, title: str = "Connections") -> str:
        """Produce Markdown table of diagram edge connections."""
        conns = self.connections()
        lines: list[str] = []
        if title:
            lines.append(f"## {title}")
            lines.append("")
        lines.append("| Source | Target | Protocol / Label | Style | Routing |")
        lines.append("| :--- | :--- | :--- | :--- | :--- |")
        for c in conns:
            src = f"**{_escape_cell(c['source_label'])}** (`{_escape_cell(c['source'])}`)"
            tgt = f"**{_escape_cell(c['target_label'])}** (`{_escape_cell(c['target'])}`)"
            proto = _escape_cell(c["protocol"]) or "-"
            style = _escape_cell(c["style"])
            routing = _escape_cell(c["routing"])
            lines.append(f"| {src} | {tgt} | {proto} | {style} | {routing} |")
        return "\n".join(lines)

    def generate_readme(
        self,
        image_file: str,
        diagram_name: Optional[str] = None,
        output_path: Union[str, Path] = "README.md",
        include_connections: bool = True,
    ) -> str:
        """Generate living documentation README with graphic link and BOM table."""
        p = Path(output_path)
        p.parent.mkdir(parents=True, exist_ok=True)

        name_val = diagram_name or getattr(
            self.diagram, "title", "IIoT Architecture"
        )
        name_str = str(name_val) if name_val is not None else "IIoT Architecture"
        clean_name = name_str.replace("_", " ")
        img_src = (
            image_file
            if (
                image_file.startswith(".")
                or image_file.startswith("/")
                or "://" in image_file
            )
            else f"./{image_file}"
        )

        sections = [
            f"# {clean_name}",
            "",
            f"![Architecture Diagram]({img_src})",
            "",
            self.to_markdown(title="Bill of Materials"),
        ]
        if include_connections and getattr(self.diagram, "edges", None):
            sections.extend(["", self.connections_to_markdown(title="Connections")])

        md_content = "\n".join(sections) + "\n"
        p.write_text(md_content, encoding="utf-8")
        return md_content
