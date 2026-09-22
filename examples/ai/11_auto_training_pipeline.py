"""Example architecture: Auto-Laid-Out Training Pipeline (AI domain)."""
from __future__ import annotations

import sys
from pathlib import Path

from diagrams_as_code import Diagram
from diagrams_as_code.output import render_all


def diagram() -> Diagram:
    with Diagram("Auto-Laid-Out Training Pipeline", theme="dracula", layout="auto") as diag:
        with diag.group("Data") as data:
            raw_lake = diag.shape("Raw Lake", icon="database")
            feature_store = diag.shape("Feature Store", icon="database")
        with diag.group("Training") as training:
            trainer = diag.shape("Trainer", icon="chip")
            tracker = diag.shape("Experiment Tracker", icon="dashboard")
        with diag.group("Serving") as serving:
            registry = diag.shape("Model Registry", icon="database")
            inference = diag.shape("Inference API", icon="api_gateway")

        raw_lake >> diag.edge("ETL") >> feature_store
        feature_store >> diag.edge("features") >> trainer
        trainer >> diag.edge("metrics") >> tracker
        trainer >> diag.edge("register") >> registry
        registry >> diag.edge("deploy") >> inference

    return diag


def build_diagram(output_dir: Path | str = "output/ai") -> Path:
    return render_all(diagram(), output_dir, "11_auto_training_pipeline")["svg"]


if __name__ == "__main__":
    dest = Path(sys.argv[1]) if len(sys.argv) > 1 else Path("output/ai")
    build_diagram(dest)
