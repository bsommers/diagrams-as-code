"""An Airflow DAG with task states and retries (DATA ENGINEERING domain).

One daily run of an orders_daily DAG. Each task instance carries a state:
success, running, up_for_retry, failed, upstream_failed, skipped or queued.
A failed extract is retried with a delay before the downstream tasks give up
(upstream_failed); a branch operator skips the full-refresh path.
"""
from __future__ import annotations

import sys
from pathlib import Path

from diagrams_as_code import Diagram, Style
from diagrams_as_code.output import render_all

SUCCESS = Style(fill="#BFE5C8", stroke="#2E7D4F", stroke_width=2.0)
RUNNING = Style(fill="#C9E7F5", stroke="#1E88C7", stroke_width=2.0)
RETRY = Style(fill="#FDE9B5", stroke="#C98A00", stroke_width=2.0)
FAILED = Style(fill="#F5C2C2", stroke="#C0392B", stroke_width=2.0)
UPSTREAM = Style(fill="#F3D9A8", stroke="#B8860B", stroke_width=2.0, dash="5,3")
SKIPPED = Style(fill="#EDE3F3", stroke="#8E6BAA", stroke_width=2.0, dash="3,3")
QUEUED = Style(fill="#E5E5E5", stroke="#7A7A7A", stroke_width=2.0)
KEY = [("success", SUCCESS), ("running", RUNNING), ("up_for_retry", RETRY), ("failed", FAILED),
       ("upstream_failed", UPSTREAM), ("skipped", SKIPPED), ("queued", QUEUED)]


def diagram() -> Diagram:
    with Diagram("Airflow DAG with Task States and Retries", theme="paper", layout="auto",
                 direction="LR", rank_gap=70, node_gap=30) as diag:
        sensor = diag.shape("wait_for_file\nS3KeySensor", 160, 54, style=SUCCESS)
        extract_a = diag.shape("extract_orders\nretry 2 of 3", 160, 54, style=RETRY)
        extract_b = diag.shape("extract_customers", 160, 54, style=SUCCESS)
        branch = diag.shape("is_full_refresh?", 160, 54, kind="diamond", style=SUCCESS)
        incr = diag.shape("load_incremental", 160, 54, style=RUNNING)
        full = diag.shape("load_full_refresh", 160, 54, style=SKIPPED)
        dbt_run = diag.shape("dbt_run", 160, 54, style=QUEUED)
        dq = diag.shape("quality_checks", 160, 54, style=UPSTREAM)
        publish = diag.shape("publish_marts", 160, 54, style=UPSTREAM)
        notify = diag.shape("slack_alert\ntrigger_rule=one_failed", 190, 54, style=FAILED)

        sensor >> diag.edge() >> extract_a
        sensor >> diag.edge() >> extract_b
        extract_a >> diag.edge() >> branch
        extract_b >> diag.edge() >> branch
        branch >> diag.edge("yes") >> full
        branch >> diag.edge("no") >> incr
        incr >> diag.edge() >> dbt_run
        full >> diag.edge() >> dbt_run
        dbt_run >> diag.edge() >> dq
        dq >> diag.edge() >> publish
        extract_a >> diag.edge("on failure", style="dashed") >> notify

        diag.caption(
            "Task-instance colours for run 2026-11-22: " + ", ".join(k for k, _ in KEY) + ".\n"
            "extract_orders is up_for_retry (retries=3, retry_delay=5 min); tasks below the "
            "running load stay queued or upstream_failed until it finishes.",
            small_caps=False,
        )
    return diag


def build_diagram(output_dir: Path | str = "examples/data_engineering") -> Path:
    return render_all(diagram(), output_dir, "02_airflow_dag_task_states")["svg"]


if __name__ == "__main__":
    dest = Path(sys.argv[1]) if len(sys.argv) > 1 else Path("examples/data_engineering")
    build_diagram(dest)
