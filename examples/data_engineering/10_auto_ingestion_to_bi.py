"""Auto-laid-out ingestion to BI path (DATA ENGINEERING domain)."""
from __future__ import annotations

import sys
from pathlib import Path

from diagrams_as_code import Diagram
from diagrams_as_code.output import render_all


def diagram() -> Diagram:
    with Diagram("Auto-Laid-Out Ingestion to BI", theme="pastel_light", layout="auto",
                 direction="LR") as diag:
        saas = diag.shape("SaaS API", icon="cloud")
        oltp = diag.shape("Orders DB", kind="cylinder")
        files = diag.shape("Partner SFTP drop", icon="document")
        fivetran = diag.shape("Managed Connector", icon="workflow")
        cdc = diag.shape("CDC Connector", icon="workflow")
        batch = diag.shape("Batch Loader", icon="workflow")
        raw = diag.shape("Raw Zone (object store)", icon="storage")
        wh = diag.shape("Warehouse", kind="cylinder")
        dbt = diag.shape("dbt Transformations", icon="workflow")
        marts = diag.shape("Marts", kind="cylinder")
        sem = diag.shape("Semantic Layer", icon="analytics")
        bi = diag.shape("BI Dashboards", icon="dashboard")
        notebook = diag.shape("Analyst Notebooks", icon="laptop")

        saas >> diag.edge("REST") >> fivetran
        oltp >> diag.edge("log stream") >> cdc
        files >> diag.edge("CSV") >> batch
        fivetran >> diag.edge() >> raw
        cdc >> diag.edge() >> raw
        batch >> diag.edge() >> raw
        raw >> diag.edge("COPY INTO") >> wh
        wh >> diag.edge() >> dbt
        dbt >> diag.edge("models") >> marts
        marts >> diag.edge() >> sem
        sem >> diag.edge() >> bi
        marts >> diag.edge("SQL") >> notebook
    return diag


def build_diagram(output_dir: Path | str = "examples/data_engineering") -> Path:
    return render_all(diagram(), output_dir, "10_auto_ingestion_to_bi")["svg"]


if __name__ == "__main__":
    dest = Path(sys.argv[1]) if len(sys.argv) > 1 else Path("examples/data_engineering")
    build_diagram(dest)
