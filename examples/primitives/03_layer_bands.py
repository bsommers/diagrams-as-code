"""Layer bands with titles and side notes (PRIM-03)."""
from __future__ import annotations

import sys
from pathlib import Path

from diagrams_as_code import Diagram, Port
from diagrams_as_code.output import render_all


def diagram() -> Diagram:
    with Diagram("Layer bands", theme="paper") as diag:
        with diag.band(
            "Application layer", notes=["Requests arrive here.", "Stateless; scale by adding replicas."],
            min_width=640,
        ) as app:
            api = diag.shape("API gateway", 130, 46).at(80, 90)
            auth = diag.shape("Auth", 110, 46).right_of(api, margin=60)
        with diag.band("Service layer", notes="Owns the business rules.", min_width=640) as svc:
            orders = diag.shape("Orders", 130, 46)
            billing = diag.shape("Billing", 110, 46).right_of(orders, margin=60)
        with diag.band("Data layer", notes="Durable state only.", min_width=640) as data:
            store = diag.shape("Order store", 130, 70, kind="cylinder")
        svc.below(app, margin=30)
        data.below(svc, margin=30)

        api >> auth
        # Attached three quarters of the way along, so the lines pass clear of the titles.
        api.anchor("bottom", 0.75) >> orders.anchor("top", 0.75)
        auth >> diag.edge(source_port=Port.SOUTH, target_port=Port.NORTH) >> billing
        orders.anchor("bottom", 0.75) >> store.anchor("top", 0.75)
        diag.caption("**Figure 3:** Three layers as dashed bands", small_caps=True)
    return diag


def build_diagram(output_dir: Path | str = "output/primitives") -> Path:
    return render_all(diagram(), output_dir, "03_layer_bands")["svg"]


if __name__ == "__main__":
    dest = Path(sys.argv[1]) if len(sys.argv) > 1 else Path("output/primitives")
    build_diagram(dest)
