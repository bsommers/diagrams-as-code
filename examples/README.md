# Diagrams-as-Code: Domain Examples Gallery

This directory contains 50 production-grade architecture and workflow diagrams spanning 5 primary domains, built entirely using the pure standard-library `iiot_diagrams` engine. Each example generates both an SVG diagram and a Bill of Materials (BOM) markdown document in `output/<domain>/`.

---

## Suite Summary & Metrics

- **Total Diagrams:** 70
- **Domains Covered:** 7 (`cloud`, `ai`, `computer`, `datacenter`, `business_process`, `cybersecurity`, `network_engineering`)
- **Diagrams per Domain:** 10
- **Themes Demonstrated:** 8 (`nord`, `emerald`, `crimson`, `monochrome`, `iiot_dark_gold`, `blueprint`, `cyber_slate`, `iiot_light`)
- **Built-in Domain Vector Icons:** 51 custom open-source SVG vector icons
- **Zero External Dependencies:** 100% Python standard library execution

---

## 1. Cloud Architecture (`examples/cloud/`)

Modern distributed, serverless, hybrid, and multi-region cloud topologies.

| # | Script & Output | Title | Theme | Complexity | Key Components / Icons |
|---|---|---|---|---|---|
| 01 | [`01_simple_vpc_web.py`](file:///home/bill/src/ai/diagrams-as-code/examples/cloud/01_simple_vpc_web.py) | Simple VPC Web Application | `nord` | Simple | ALB, Web Servers, Multi-AZ PostgreSQL |
| 02 | [`02_serverless_event_pipeline.py`](file:///home/bill/src/ai/diagrams-as-code/examples/cloud/02_serverless_event_pipeline.py) | Serverless Event Pipeline | `cyber_slate` | Moderate | API Gateway, Event Hub, Serverless Functions, S3 |
| 03 | [`03_cdn_multi_region_edge.py`](file:///home/bill/src/ai/diagrams-as-code/examples/cloud/03_cdn_multi_region_edge.py) | CDN & Multi-Region Edge Topology | `blueprint` | Advanced | Anycast DNS, Global CDN Edge, Region Primary & Secondary |
| 04 | [`04_hybrid_cloud_vpn.py`](file:///home/bill/src/ai/diagrams-as-code/examples/cloud/04_hybrid_cloud_vpn.py) | Hybrid Cloud VPN Architecture | `iiot_dark_gold` | Moderate | Customer Gateway, IPSec VPN, VPC Ingress, File Storage |
| 05 | [`05_microservices_service_mesh.py`](file:///home/bill/src/ai/diagrams-as-code/examples/cloud/05_microservices_service_mesh.py) | Microservices Service Mesh | `emerald` | Advanced | Ingress Controller, Auth, Orders, Payments, Mesh Control |
| 06 | [`06_multi_cloud_dr_failover.py`](file:///home/bill/src/ai/diagrams-as-code/examples/cloud/06_multi_cloud_dr_failover.py) | Multi-Cloud Disaster Recovery | `crimson` | Enterprise | Global DNS Traffic, AWS Primary VPC, Azure Secondary VNet |
| 07 | [`07_data_lakehouse_ingest.py`](file:///home/bill/src/ai/diagrams-as-code/examples/cloud/07_data_lakehouse_ingest.py) | Cloud Data Lakehouse Ingestion | `monochrome` | Advanced | Kafka Streaming, Ingest Workers, Bronze/Silver/Gold Lakehouse |
| 08 | [`08_zero_trust_ingress_security.py`](file:///home/bill/src/ai/diagrams-as-code/examples/cloud/08_zero_trust_ingress_security.py) | Zero Trust Ingress Security Stack | `cyber_slate` | Enterprise | WAF/DDoS Shield, Mutual TLS Gateway, IdP, Internal Apps |
| 09 | [`09_iot_cloud_fleet_management.py`](file:///home/bill/src/ai/diagrams-as-code/examples/cloud/09_iot_cloud_fleet_management.py) | Global IoT Cloud Fleet Management | `nord` | Advanced | Edge Gateways, MQTT Ingestion Broker, TimeSeries DB, Telemetry |
| 10 | [`10_global_enterprise_backbone.py`](file:///home/bill/src/ai/diagrams-as-code/examples/cloud/10_global_enterprise_backbone.py) | Global Cloud Enterprise Backbone | `iiot_dark_gold` | Enterprise | Cloud WAN Hub, Direct Connect, Enterprise VPCs, Multi-Region Transit |

---

## 2. Artificial Intelligence & Machine Learning (`examples/ai/`)

Large language model pipelines, autonomous agent swarms, vector retrieval, distributed training clusters, and robotics SLAM architectures.

| # | Script & Output | Title | Theme | Complexity | Key Components / Icons |
|---|---|---|---|---|---|
| 01 | [`01_simple_rag_pipeline.py`](file:///home/bill/src/ai/diagrams-as-code/examples/ai/01_simple_rag_pipeline.py) | Simple Retrieval-Augmented Generation (RAG) | `nord` | Moderate | Embedding Model, Vector DB (HNSW), Foundation LLM |
| 02 | [`02_multimodal_vision_inference.py`](file:///home/bill/src/ai/diagrams-as-code/examples/ai/02_multimodal_vision_inference.py) | Multimodal Vision Inference Service | `cyber_slate` | Moderate | Camera Stream, Preprocessing, Vision-Language Model, Detection Cache |
| 03 | [`03_agentic_tool_orchestration.py`](file:///home/bill/src/ai/diagrams-as-code/examples/ai/03_agentic_tool_orchestration.py) | Agentic Tool-Use Orchestration Framework | `emerald` | Advanced | Supervisor Agent, Search Tool, Code Sandbox, SQL Tool, Memory Store |
| 04 | [`04_distributed_training_cluster.py`](file:///home/bill/src/ai/diagrams-as-code/examples/ai/04_distributed_training_cluster.py) | Distributed LLM Training Cluster | `crimson` | Enterprise | Master Coordinator, Multi-GPU Worker Nodes, High-Speed NVLink/InfiniBand Fabric |
| 05 | [`05_feature_store_mlops.py`](file:///home/bill/src/ai/diagrams-as-code/examples/ai/05_feature_store_mlops.py) | Enterprise Feature Store & MLOps Pipeline | `blueprint` | Advanced | Batch & Stream Ingest, Online Redis, Offline Parquet, Model Registry |
| 06 | [`06_fine_tuning_lora_pipeline.py`](file:///home/bill/src/ai/diagrams-as-code/examples/ai/06_fine_tuning_lora_pipeline.py) | Parameter-Efficient Fine-Tuning (LoRA) Pipeline | `nord` | Moderate | Curated Dataset, Frozen Base LLM, LoRA Adapter Weights, Evaluation Harness |
| 07 | [`07_enterprise_knowledge_graph_llm.py`](file:///home/bill/src/ai/diagrams-as-code/examples/ai/07_enterprise_knowledge_graph_llm.py) | Enterprise GraphRAG Knowledge Architecture | `iiot_dark_gold` | Advanced | Triplet Extractor, Entity Graph Store, Hybrid Vector/Graph Retriever, LLM |
| 08 | [`08_ai_guardrails_safety_eval.py`](file:///home/bill/src/ai/diagrams-as-code/examples/ai/08_ai_guardrails_safety_eval.py) | AI Safety & Alignment Guardrail Filter | `cyber_slate` | Moderate | Prompt Injection Filter, PII Masking, LLM Core, Hallucination Scorer |
| 09 | [`09_autonomous_robotics_slam.py`](file:///home/bill/src/ai/diagrams-as-code/examples/ai/09_autonomous_robotics_slam.py) | Autonomous Mobile Robot SLAM & Perception Stack | `emerald` | Enterprise | LiDAR & Stereo Depth, Visual Odometry, EKF State Estimator, Costmap Planner |
| 10 | [`10_self_hosted_vllm_cluster.py`](file:///home/bill/src/ai/diagrams-as-code/examples/ai/10_self_hosted_vllm_cluster.py) | High-Throughput vLLM Serving Cluster | `monochrome` | Advanced | Reverse Proxy Router, PagedAttention vLLM Workers, Model Storage Cache |

---

## 3. Computer & Edge Systems (`examples/computer/`)

Workstations, home labs, embedded RTOS, industrial PLCs, edge gateways, and developer environments.

| # | Script & Output | Title | Theme | Complexity | Key Components / Icons |
|---|---|---|---|---|---|
| 01 | [`01_workstation_peripherals.py`](file:///home/bill/src/ai/diagrams-as-code/examples/computer/01_workstation_peripherals.py) | Developer Workstation & Peripheral Bus | `nord` | Simple | Host Tower, Thunderbolt Dock, Dual Displays, NVMe External |
| 02 | [`02_home_lab_network.py`](file:///home/bill/src/ai/diagrams-as-code/examples/computer/02_home_lab_network.py) | Home Lab Server Topology | `blueprint` | Moderate | Core Router/Firewall, Managed PoE Switch, Proxmox Hypervisor, TrueNAS |
| 03 | [`03_plc_industrial_io.py`](file:///home/bill/src/ai/diagrams-as-code/examples/computer/03_plc_industrial_io.py) | Industrial PLC & Remote I/O Bus | `iiot_dark_gold` | Moderate | Allen-Bradley/Siemens PLC, Remote I/O Racks, Modbus RTU Sensor Array |
| 04 | [`04_dual_homed_edge_gateway.py`](file:///home/bill/src/ai/diagrams-as-code/examples/computer/04_dual_homed_edge_gateway.py) | Dual-Homed Industrial Edge Gateway | `cyber_slate` | Advanced | OT Industrial Subnet, Edge Gateway Appliance, IT Corporate Network |
| 05 | [`05_developer_terminal_environment.py`](file:///home/bill/src/ai/diagrams-as-code/examples/computer/05_developer_terminal_environment.py) | Modern Developer Terminal & Tooling Stack | `monochrome` | Simple | Terminal Emulator, Multiplexer, Neovim/LSP, Container Runtime |
| 06 | [`06_mobile_client_sync.py`](file:///home/bill/src/ai/diagrams-as-code/examples/computer/06_mobile_client_sync.py) | Mobile Device Edge Synchronization | `emerald` | Moderate | iOS/Android Clients, Local SQLite/WatermelonDB, Sync Gateway, Cloud Datastore |
| 07 | [`07_embedded_rtos_system.py`](file:///home/bill/src/ai/diagrams-as-code/examples/computer/07_embedded_rtos_system.py) | Real-Time Embedded Microcontroller Architecture | `nord` | Advanced | ARM Cortex-M7, FreeRTOS Scheduler, Sensor Tasks, CAN-FD Transceiver |
| 08 | [`08_vdi_thin_client_fleet.py`](file:///home/bill/src/ai/diagrams-as-code/examples/computer/08_vdi_thin_client_fleet.py) | Enterprise Virtual Desktop (VDI) Thin Client Fleet | `blueprint` | Enterprise | Thin Client Terminals, Secure Gateway, VDI Connection Broker, Hyper-V Host |
| 09 | [`09_scada_hmi_control_station.py`](file:///home/bill/src/ai/diagrams-as-code/examples/computer/09_scada_hmi_control_station.py) | SCADA Supervisory HMI Station | `iiot_dark_gold` | Advanced | Dual HMI Displays, Industrial PC, Redundant SCADA Servers, Plant Network |
| 10 | [`10_high_performance_workstation_storage.py`](file:///home/bill/src/ai/diagrams-as-code/examples/computer/10_high_performance_workstation_storage.py) | High-Performance Workstation NVMe Storage Tier | `crimson` | Advanced | Threadripper CPU, PCIe Gen5 Switch, U.2 NVMe RAID Array, 100GbE NIC |

---

## 4. Datacenter Infrastructure (`examples/datacenter/`)

High-density compute pods, SAN fabrics, leaf-spine network fabrics, power distribution, and concurrently maintainable Tier IV designs.

| # | Script & Output | Title | Theme | Complexity | Key Components / Icons |
|---|---|---|---|---|---|
| 01 | [`01_single_rack_blade_chassis.py`](file:///home/bill/src/ai/diagrams-as-code/examples/datacenter/01_single_rack_blade_chassis.py) | 42U Server Rack & Blade Chassis | `blueprint` | Moderate | Top-of-Rack (ToR) Switch, Dual PDUs, Blade Enclosure, Storage Shelves |
| 02 | [`02_san_storage_fabric.py`](file:///home/bill/src/ai/diagrams-as-code/examples/datacenter/02_san_storage_fabric.py) | Fibre Channel Storage Area Network (SAN) | `nord` | Advanced | Compute Hosts, Fabric A Brocade Switch, Fabric B Brocade Switch, All-Flash Array |
| 03 | [`03_leaf_spine_clos_network.py`](file:///home/bill/src/ai/diagrams-as-code/examples/datacenter/03_leaf_spine_clos_network.py) | Leaf-Spine Clos Network Fabric | `cyber_slate` | Enterprise | Spine Switches 01-04, Leaf Switches 01-04, Server Racks with EVPN-VXLAN |
| 04 | [`04_power_distribution_ups.py`](file:///home/bill/src/ai/diagrams-as-code/examples/datacenter/04_power_distribution_ups.py) | Datacenter 2N Power Distribution & UPS | `crimson` | Enterprise | Utility Feed, Diesel Generator, Dual Rotary UPS A/B, STS, Floor PDUs |
| 05 | [`05_hvac_containment_cooling.py`](file:///home/bill/src/ai/diagrams-as-code/examples/datacenter/05_hvac_containment_cooling.py) | Hot/Cold Aisle Containment & CRAC Units | `emerald` | Moderate | Chilled Water Chiller, CRAC Units A & B, Cold Aisle Plenum, Server Inlets |
| 06 | [`06_kubernetes_bare_metal.py`](file:///home/bill/src/ai/diagrams-as-code/examples/datacenter/06_kubernetes_bare_metal.py) | Bare-Metal Kubernetes Infrastructure Pod | `nord` | Advanced | Control Plane Nodes (etcd), Calico BGP ToR Switch, Worker Compute Nodes |
| 07 | [`07_disaster_recovery_datacenter_pair.py`](file:///home/bill/src/ai/diagrams-as-code/examples/datacenter/07_disaster_recovery_datacenter_pair.py) | Active-Active Datacenter Replication Pair | `blueprint` | Enterprise | Primary Metro DC, Secondary Remote DC, Dark Fiber DCI, Storage Replication |
| 08 | [`08_high_density_ai_compute_pod.py`](file:///home/bill/src/ai/diagrams-as-code/examples/datacenter/08_high_density_ai_compute_pod.py) | High-Density AI GPU SuperPOD Architecture | `iiot_dark_gold` | Enterprise | In-Row Liquid Cooling CDU, 8x NVIDIA HGX Nodes, Quantum InfiniBand Fabric |
| 09 | [`09_edge_micro_datacenter.py`](file:///home/bill/src/ai/diagrams-as-code/examples/datacenter/09_edge_micro_datacenter.py) | Ruggedized Edge Micro-Datacenter (MDC) | `cyber_slate` | Moderate | NEMA-4 Enclosure, Edge Converged Host, Integrated Lithium UPS, LTE Failover |
| 10 | [`10_tier4_concurrently_maintainable.py`](file:///home/bill/src/ai/diagrams-as-code/examples/datacenter/10_tier4_concurrently_maintainable.py) | Tier IV Concurrently Maintainable Datacenter | `monochrome` | Enterprise | Dual Substation Feeds, Independent Power Paths A/B, Isolated Cooling Loops |

---

## 5. Business Processes & Operational Workflows (`examples/business_process/`)

Cross-functional enterprise workflows, approval gates, compliance audits, procurement, and automated fraud triage.

| # | Script & Output | Title | Theme | Complexity | Key Components / Icons |
|---|---|---|---|---|---|
| 01 | [`01_order_to_cash.py`](file:///home/bill/src/ai/diagrams-as-code/examples/business_process/01_order_to_cash.py) | Order-to-Cash (O2C) Enterprise Workflow | `emerald` | Moderate | Customer Ingestion, Credit Check Gate, ERP Inventory Allocation, Invoicing |
| 02 | [`02_employee_onboarding.py`](file:///home/bill/src/ai/diagrams-as-code/examples/business_process/02_employee_onboarding.py) | Enterprise Employee Onboarding Lifecycle | `nord` | Moderate | Offer Acceptance, HR Record Creation, IT Identity Provisioning, Day One Induction |
| 03 | [`03_it_incident_escalation.py`](file:///home/bill/src/ai/diagrams-as-code/examples/business_process/03_it_incident_escalation.py) | IT Major Incident Escalation & Response | `crimson` | Advanced | Alert Ingestion, Tier 1 Triage, Incident Commander War Room, RCA Post-Mortem |
| 04 | [`04_procure_to_pay.py`](file:///home/bill/src/ai/diagrams-as-code/examples/business_process/04_procure_to_pay.py) | Procure-to-Pay (P2P) Purchasing Process | `blueprint` | Advanced | Requisition Submission, VP Budget Approval, Vendor PO Issuance, 3-Way Match |
| 05 | [`05_regulatory_compliance_audit.py`](file:///home/bill/src/ai/diagrams-as-code/examples/business_process/05_regulatory_compliance_audit.py) | SOC 2 / ISO 27001 Compliance Audit Workflow | `iiot_dark_gold` | Advanced | Control Evidence Collection, Auditor Sampling Review, Remediation Ticket, Report |
| 06 | [`06_software_release_gate.py`](file:///home/bill/src/ai/diagrams-as-code/examples/business_process/06_software_release_gate.py) | Automated Production Software Release Gate | `cyber_slate` | Moderate | Commit Tagging, Static Security Analysis (SAST), Canary Deploy, Rollback Gate |
| 07 | [`07_customer_loan_origination.py`](file:///home/bill/src/ai/diagrams-as-code/examples/business_process/07_customer_loan_origination.py) | Customer Loan Origination & Underwriting | `emerald` | Enterprise | Online Application, Automated Credit Scoring Engine, Underwriter Review, Disbursement |
| 08 | [`08_supply_chain_rfq_fulfillment.py`](file:///home/bill/src/ai/diagrams-as-code/examples/business_process/08_supply_chain_rfq_fulfillment.py) | Supply Chain RFQ & Supplier Selection | `blueprint` | Advanced | Bill of Materials Intake, Vendor Bidding Portal, Cost/Lead-Time Matrix, Contract Award |
| 09 | [`09_claims_processing_fraud_detection.py`](file:///home/bill/src/ai/diagrams-as-code/examples/business_process/09_claims_processing_fraud_detection.py) | Insurance Claims Triage & Fraud Detection | `crimson` | Enterprise | FNOL Filing, ML Fraud Score Model, Special Investigation Unit (SIU), Fast-Track Pay |
| 10 | [`10_enterprise_change_management.py`](file:///home/bill/src/ai/diagrams-as-code/examples/business_process/10_enterprise_change_management.py) | Enterprise ITIL Change Advisory Board (CAB) | `monochrome` | Advanced | Change Request (RFC), Risk Assessment Matrix, CAB Review Meeting, Scheduled Maintenance |

---

## 6. Cybersecurity Architecture (`examples/cybersecurity/`)

Threat hunting, Zero Trust access, SIEM/SOAR telemetry, PKI trust hierarchy, secrets management, and air-gapped recovery vaults.

| # | Script & Output | Title | Theme | Complexity | Key Components / Icons |
|---|---|---|---|---|---|
| 01 | [`01_perimeter_defense_dmz.py`](file:///home/bill/src/ai/diagrams-as-code/examples/cybersecurity/01_perimeter_defense_dmz.py) | Enterprise DMZ Perimeter Defense | `crimson` | Moderate | Web Client, External Firewall, Reverse Proxy, WAF Inspector, Internal mTLS |
| 02 | [`02_soc_siem_pipeline.py`](file:///home/bill/src/ai/diagrams-as-code/examples/cybersecurity/02_soc_siem_pipeline.py) | SOC & SIEM Telemetry Analytics Pipeline | `cyber_slate` | Advanced | EDR Fleet, Firewall Syslog, CloudTrail, Log Aggregator, SIEM ML, SOAR |
| 03 | [`03_zero_trust_ztna.py`](file:///home/bill/src/ai/diagrams-as-code/examples/cybersecurity/03_zero_trust_ztna.py) | Zero Trust Network Access (ZTNA) Architecture | `nord` | Advanced | Remote Employee, Device Posture Agent, Enterprise IdP, ZTNA Policy Broker, App Gateway |
| 04 | [`04_pki_ca_hierarchy.py`](file:///home/bill/src/ai/diagrams-as-code/examples/cybersecurity/04_pki_ca_hierarchy.py) | Public Key Infrastructure (PKI) Certificate Hierarchy | `blueprint` | Advanced | Offline Root CA (HSM), TLS Issuing CA, Code Signing CA, OCSP Responder, End Entities |
| 05 | [`05_edr_threat_hunting.py`](file:///home/bill/src/ai/diagrams-as-code/examples/cybersecurity/05_edr_threat_hunting.py) | Endpoint Detection & Threat Hunting Grid | `crimson` | Advanced | Managed OS Endpoints, Telemetry Ingestion Hub, ATT&CK Correlator, SOC Lead, Host Isolation |
| 06 | [`06_secrets_vault_rotation.py`](file:///home/bill/src/ai/diagrams-as-code/examples/cybersecurity/06_secrets_vault_rotation.py) | Automated Secrets Vault & Credential Rotation | `emerald` | Advanced | Kubernetes Pod, HashiCorp Vault, FIPS HSM Core, Rotation Controller, Postgres |
| 07 | [`07_honeynet_deception_grid.py`](file:///home/bill/src/ai/diagrams-as-code/examples/cybersecurity/07_honeynet_deception_grid.py) | Deception Technology Honeynet Grid | `cyber_slate` | Advanced | Adversary Terminal, Decoy SSH Bastion, Decoy Admin Portal, Honeytoken DB, BGP Sinkhole |
| 08 | [`08_ids_ips_inline_inspection.py`](file:///home/bill/src/ai/diagrams-as-code/examples/cybersecurity/08_ids_ips_inline_inspection.py) | Inline IDS/IPS Deep Packet Inspection | `iiot_dark_gold` | Enterprise | Border Router, Network Packet Broker TAP, ASIC SSL Decryptor, Suricata IPS, Core Switch |
| 09 | [`09_iam_federation_saml_oidc.py`](file:///home/bill/src/ai/diagrams-as-code/examples/cybersecurity/09_iam_federation_saml_oidc.py) | Enterprise IAM Federation & SSO Pipeline | `monochrome` | Moderate | Corporate User, FIDO2 WebAuthn Key, Okta/Entra IdP, LDAP/AD, SaaS App, OIDC Portal |
| 10 | [`10_ransomware_containment_airgap.py`](file:///home/bill/src/ai/diagrams-as-code/examples/cybersecurity/10_ransomware_containment_airgap.py) | Ransomware Defense & Optical Air-Gapped Vault | `crimson` | Enterprise | Production SAN, Backup Master, Optical Data Diode (Tx-Only), Immutable WORM Vault, Cleanroom Sandbox |

---

## 7. Network Engineering (`examples/network_engineering/`)

Campus LAN switching, multihomed BGP peering, provider MPLS L3VPN, EVPN-VXLAN datacenter fabrics, SD-WAN, and DWDM optical transport.

| # | Script & Output | Title | Theme | Complexity | Key Components / Icons |
|---|---|---|---|---|---|
| 01 | [`01_three_tier_campus_lan.py`](file:///home/bill/src/ai/diagrams-as-code/examples/network_engineering/01_three_tier_campus_lan.py) | Three-Tier Hierarchical Campus LAN | `blueprint` | Moderate | Core Switch Pair, Distribution Switch Pair, Floor Access Switches (PoE++) |
| 02 | [`02_bgp_dual_multihomed_wan.py`](file:///home/bill/src/ai/diagrams-as-code/examples/network_engineering/02_bgp_dual_multihomed_wan.py) | Dual-Homed eBGP Enterprise WAN Peering | `cyber_slate` | Advanced | Tier-1 Transit ISPs (AS 174, AS 2914), Edge Core Routers, iBGP Full Mesh, Core Fabric |
| 03 | [`03_mpls_vpn_backbone.py`](file:///home/bill/src/ai/diagrams-as-code/examples/network_engineering/03_mpls_vpn_backbone.py) | MPLS Layer 3 VPN Service Provider Backbone | `iiot_dark_gold` | Enterprise | Customer Edge (CE) Routers, Provider Edge (PE) Routers, 400G P Core LSRs, VRF Segmentation |
| 04 | [`04_vxlan_evpn_datacenter_fabric.py`](file:///home/bill/src/ai/diagrams-as-code/examples/network_engineering/04_vxlan_evpn_datacenter_fabric.py) | EVPN-VXLAN Datacenter Spine-Leaf Fabric | `nord` | Enterprise | 400G Spine Switches, Leaf VTEP Switches, MLAG Server Dual-Homing, VXLAN VNIs |
| 05 | [`05_sd_wan_hub_and_spoke.py`](file:///home/bill/src/ai/diagrams-as-code/examples/network_engineering/05_sd_wan_hub_and_spoke.py) | Enterprise SD-WAN Hub-and-Spoke Topology | `emerald` | Advanced | vManage Orchestrator, vSmart OMP Controller, HQ Hub Router, Branch Office Appliances |
| 06 | [`06_ha_firewall_cluster_carp_sync.py`](file:///home/bill/src/ai/diagrams-as-code/examples/network_engineering/06_ha_firewall_cluster_carp_sync.py) | High-Availability Active/Passive Firewall Cluster | `crimson` | Advanced | WAN Switch (CARP VIP), Active/Passive Firewall Pair, Dedicated pfsync Heartbeat, LAN Switch |
| 07 | [`07_dwdm_metro_optical_ring.py`](file:///home/bill/src/ai/diagrams-as-code/examples/network_engineering/07_dwdm_metro_optical_ring.py) | Metro DWDM Optical Transport Ring | `blueprint` | Enterprise | Metro West/East/South ROADMs (96 Waves), 144F Optical Patch Bay, 100G Muxponder |
| 08 | [`08_ospf_multi_area_enterprise.py`](file:///home/bill/src/ai/diagrams-as-code/examples/network_engineering/08_ospf_multi_area_enterprise.py) | OSPF Multi-Area Enterprise Routing | `monochrome` | Advanced | Area 0 Backbone Core Routers, Area 10 Campus ABR, Datacenter ASBR, BGP Redistribution |
| 09 | [`09_radius_802_1x_nac.py`](file:///home/bill/src/ai/diagrams-as-code/examples/network_engineering/09_radius_802_1x_nac.py) | 802.1X Network Access Control (NAC) & RADIUS | `nord` | Moderate | Supplicant Laptop, 802.1X Authenticator Switch, FreeRADIUS/ISE, Active Directory, Dynamic VLANs |
| 10 | [`10_dns_anycast_authoritative_mesh.py`](file:///home/bill/src/ai/diagrams-as-code/examples/network_engineering/10_dns_anycast_authoritative_mesh.py) | Global Anycast Authoritative DNS Network | `cyber_slate` | Enterprise | Global DNS Clients, US-East & EU-Central BGP Anycast PoPs, Knot/BIND Resolvers, Master Zone DB |

---

## Executing the Gallery

To regenerate all diagrams and documentation artifacts across all domains:

```bash
uv run python -c "
import subprocess, glob, sys
for script in sorted(glob.glob('examples/*/*.py')):
    print(f'Building {script}...')
    subprocess.run([sys.executable, script], check=True)
"
```

To run automated verification tests across the entire gallery:

```bash
uv run pytest tests/test_domain_examples.py
```

