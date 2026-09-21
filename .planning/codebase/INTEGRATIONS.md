---
last_mapped_commit: aa12f844a5d25922af7be204ce6e5ef29d89db57
---

# External Integrations

**Analysis Date:** 2026-09-19

## APIs & External Services

**Cloud Storage:**
- AWS S3 - Hosting and distribution of generated diagram graphics (`*.svg`, `*.png`) and markdown documentation
  - SDK/Client: `boto3` v1.x (`boto3.client('s3')`)
  - Implementation: `upload_to_s3()` in `iiot_theme.py`
  - Auth: `AWS_ACCESS_KEY_ID`, `AWS_SECRET_ACCESS_KEY` environment variables (configured via `docker-compose.yml`)

**Version Control Services:**
- GitHub / Remote Git - Automated synchronization of generated diagrams and README Bill of Materials
  - SDK/Client: `gitpython` (`git.Repo`)
  - Implementation: `push_to_github()` in `iiot_theme.py`
  - Auth: Local git SSH keys or credential helper

## Data Storage

**File Systems & Local Catalogs:**
- Local Icon Catalog (`icons/icons.yaml`, `icons/icons.csv`)
  - Schema: `symbol`, `path`, `notes`
  - Loaded by `IIoTPalette.load_icons()` in `iiot_theme.py`

## Protocol & Ecosystem Mappings

**Industrial IoT (IIoT) Ecosystem:**
- The codebase models IIoT architecture components across multiple diagram definitions:
  - Brokers & Clusters: IIoT Edge Gateway, Central IIoT Cluster (`diagram-sparklplug.py`, `diagram-iiot-high-availability.py`)
  - Field Protocols: Modbus/TCP, OPC UA, Sparkplug B (`spBv1.0/...`), MQTT over TLS
  - Data Streaming & Historians: Apache Kafka (`diagrams.onprem.queue.Kafka`), InfluxDB (`diagrams.onprem.database.Influxdb`)
  - Observability: Grafana Cloud dashboards (`diagrams.onprem.monitoring.Grafana`)

## Webhooks & Notifications

- None configured directly in code; intended for execution within CI/CD pipelines (e.g., GitHub Actions referenced in `RUNNING.md`).
