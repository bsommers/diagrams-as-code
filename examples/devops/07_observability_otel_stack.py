"""Example architecture: observability stack around an OpenTelemetry Collector (DEVOPS domain)."""
from __future__ import annotations

import sys
from pathlib import Path

from diagrams_as_code import Diagram, Edge, Group, Shape
from diagrams_as_code.output import render_all


def diagram() -> Diagram:
    with Diagram("Observability Stack: Metrics, Logs and Traces via the OpenTelemetry Collector", theme="paper") as diag:
        with diag.group("Telemetry sources") as sources:
            app = diag.add(Shape("app", "Services with OTel SDK", width=190, icon="server", signals="traces, metrics, logs"))
            infra = diag.add(Shape("infra", "Nodes and Kubelet", width=190, icon="cluster", signals="host and pod metrics"))
            files = diag.add(Shape("files", "Container Log Files", width=190, icon="document", signals="stdout / stderr"))
            app.at(30, 60)
            infra.at(30, 165)
            files.at(30, 270)

        with diag.group("OpenTelemetry Collector (agent + gateway)") as collector:
            rcv = diag.add(Shape("rcv", "Receivers\nOTLP, prometheus, filelog", width=160, height=300, icon="api_gateway"))
            proc = diag.add(Shape("proc", "Processors\nmemory_limiter, k8sattributes,\nresource, batch", width=160, height=300, icon="analytics"))
            exp = diag.add(Shape("exp", "Exporters\nOTLP, remote_write, loki", width=160, height=300, icon="gateway"))
            rcv.at(30, 60)
            proc.right_of(rcv, margin=90)
            exp.right_of(proc, margin=90)

        with diag.group("Storage backends") as backends:
            logs = diag.add(Shape("logs", "Loki", width=170, icon="storage", signal="logs"))
            traces = diag.add(Shape("traces", "Tempo", width=170, icon="storage", signal="traces"))
            metrics = diag.add(Shape("metrics", "Prometheus / Mimir", width=170, icon="database", signal="metrics"))
            logs.at(30, 60)
            traces.at(30, 165)
            metrics.at(30, 270)

        with diag.group("Visualise") as viz:
            grafana = diag.add(Shape("grafana", "Grafana", width=150, height=300, icon="dashboard",
                                     role="dashboards, explore, trace-to-logs"))
            grafana.at(30, 60)
        alert = diag.add(Shape("alert", "Alertmanager", width=170, icon="message", routes="group, silence, route"))
        pager = diag.add(Shape("pager", "On-call Pager", width=150, icon="mobile", duty="primary / secondary"))

        sources.at(40, 60)
        collector.right_of(sources, margin=80, align="top")
        backends.right_of(collector, margin=80, align="top")
        viz.right_of(backends, margin=70, align="top")
        alert.below(backends, margin=50)
        pager.right_of(alert, margin=70)

        diag.connect(app, rcv.anchor("left", 0.1), label="OTLP", routing="direct")
        diag.connect(infra, rcv.anchor("left", 0.45), label="scrape", routing="direct")
        diag.connect(files, rcv.anchor("left", 0.8), label="tail", routing="direct")
        rcv >> diag.edge("pipeline", style="solid") >> proc
        proc >> diag.edge("batched", style="solid") >> exp
        diag.connect(exp.anchor("right", 0.1), logs, label="push", routing="direct")
        diag.connect(exp.anchor("right", 0.45), traces, label="OTLP", routing="direct")
        diag.connect(exp.anchor("right", 0.8), metrics, label="remote write", routing="direct")
        diag.connect(logs, grafana.anchor("left", 0.1), label="LogQL", routing="direct")
        diag.connect(traces, grafana.anchor("left", 0.45), label="TraceQL", routing="direct")
        diag.connect(metrics, grafana.anchor("left", 0.8), label="PromQL", routing="direct")
        metrics >> diag.edge("alert rules fire", style="dashed", color="#B03A2E", source_port="south") >> alert
        alert >> diag.edge("page", style="dashed", color="#B03A2E") >> pager

    return diag


def build_diagram(output_dir: Path | str = "examples/devops") -> Path:
    return render_all(diagram(), output_dir, "07_observability_otel_stack")["svg"]


if __name__ == "__main__":
    dest = Path(sys.argv[1]) if len(sys.argv) > 1 else Path("examples/devops")
    build_diagram(dest)
