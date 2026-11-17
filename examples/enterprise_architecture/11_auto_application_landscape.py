"""Example architecture: Auto-Laid-Out Application Landscape (ENTERPRISE_ARCHITECTURE domain)."""
from __future__ import annotations

import sys
from pathlib import Path

from diagrams_as_code import Diagram
from diagrams_as_code.output import render_all


def diagram() -> Diagram:
    with Diagram("Auto-Laid-Out Retail Application Landscape", theme="dracula", layout="auto") as diag:
        web_shop = diag.shape("Web Shop", icon="laptop")
        store_pos = diag.shape("Store POS", icon="terminal")
        api_gateway = diag.shape("API Gateway", icon="api_gateway")
        order_mgmt = diag.shape("Order Management", icon="workflow")
        crm = diag.shape("CRM", icon="user")
        erp = diag.shape("ERP", icon="server")
        warehouse = diag.shape("Warehouse Mgmt", icon="storage")
        data_platform = diag.shape("Data Platform", icon="database")

        web_shop >> diag.edge("orders") >> api_gateway
        store_pos >> diag.edge("sales") >> api_gateway
        api_gateway >> diag.edge() >> order_mgmt
        api_gateway >> diag.edge("loyalty") >> crm
        order_mgmt >> diag.edge("invoices") >> erp
        order_mgmt >> diag.edge("picks") >> warehouse
        erp >> diag.edge() >> data_platform
        warehouse >> diag.edge("stock") >> data_platform

    return diag


def build_diagram(output_dir: Path | str = "output/enterprise_architecture") -> Path:
    return render_all(diagram(), output_dir, "11_auto_application_landscape")["svg"]


if __name__ == "__main__":
    dest = Path(sys.argv[1]) if len(sys.argv) > 1 else Path("output/enterprise_architecture")
    build_diagram(dest)
