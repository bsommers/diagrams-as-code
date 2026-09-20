# Industrial IoT (IIoT) Diagrams-as-Code

A pure-Python, zero-Graphviz directed diagrams engine tailored for Industrial IoT, edge computing, and enterprise Unified Namespace (UNS) architectures.

## Reference Architecture

![Architecture Diagram](output/main_architecture.svg)

## Key Features

- **Pure-Python & Lightweight**: No Graphviz, Cairo, or external C-library runtime dependencies required for SVG generation.
- **Decoupled Architecture**: Elements exist independently of canvas layout; position constraints (`at`, `below`, `right_of`, `align`) can be applied late or dynamically updated.
- **Hierarchical Auto-Bounding**: Container groups dynamically calculate bounds enclosing child shapes with configurable padding and header room.
- **Orthogonal Manhattan Routing**: Smart directional routing between element ports (`Port.NORTH`, `Port.EAST`, etc.) with collision avoidance and embedded protocol badges.
- **Automated Living Documentation**: Instant generation of Markdown Bill of Materials (BOM), connection tables, and JSON metadata.
- **Vector Shape & Icon Library**: Built-in crisp SVG primitives (box, cylinder, server rack, database, diamond) and IIoT vector icons (sensor, gateway, broker, queue, database, dashboard).

## Quickstart

### Installation

```bash
# Provision virtualenv and install dependencies
uv sync
```

### Generating Diagrams

Generate the reference architecture diagram and living documentation:

```bash
uv run python main.py
```

### Running Examples

```bash
uv run python examples/01_mockup_slide.py
uv run python examples/02_high_availability.py
uv run python examples/03_sparkplug_pipeline.py
```

### Running Test Suite

```bash
uv run pytest
```


---

## Bill of Materials (BOM)

| Symbol / ID | Label | Kind | Group | Technical Notes / Metadata |
| :--- | :--- | :--- | :--- | :--- |
| `shape_2` | **Automation PLC** | box | Plant Floor (Edge Tier) | vendor: Siemens S7-1500, protocol: OPC UA |
| `shape_3` | **IIoT Edge Gateway** | box | Plant Floor (Edge Tier) | software: Node-RED / Ignition Edge, specs: 4-Core IPC |
| `shape_5` | **Enterprise MQTT Broker** | server_rack | Cloud Platform (UNS Tier) | engine: Enterprise MQTT Broker Cluster, ha: 3-Node Multi-AZ |
| `shape_6` | **Time-Series Database** | database | Cloud Platform (UNS Tier) | engine: InfluxDB Enterprise, retention: 365 Days |
| `shape_8` | **Executive Dashboard** | box | Enterprise Operations | platform: Grafana Enterprise, kpis: OEE / MTBF / Scada |

---

## Connections & Telemetry Protocols

| Source | Target | Protocol / Label | Style | Routing |
| :--- | :--- | :--- | :--- | :--- |
| **Automation PLC** (`shape_2`) | **IIoT Edge Gateway** (`shape_3`) | OPC UA / Modbus | solid | orthogonal |
| **Enterprise MQTT Broker** (`shape_5`) | **Time-Series Database** (`shape_6`) | Historian Ingest | solid | orthogonal |
| **IIoT Edge Gateway** (`shape_3`) | **Enterprise MQTT Broker** (`shape_5`) | Secure TLS Bridge | solid | orthogonal |
| **Enterprise MQTT Broker** (`shape_5`) | **Executive Dashboard** (`shape_8`) | Analytics Stream | solid | orthogonal |
