# Diagrams-as-Code: Domain Examples Gallery

This directory contains 143 production-grade architecture, workflow and technical diagrams spanning 13 primary domains, built entirely using the pure standard-library `diagrams_as_code` engine. Each example generates an SVG vector graphic, PNG rasterized image, and Bill of Materials (BOM) markdown document in `examples/<domain>/`.

---

## Suite Summary & Metrics

- **Total Diagrams:** 143
- **Domains Covered:** 13 (`cloud`, `ai`, `computer`, `datacenter`, `business_process`, `cybersecurity`, `network_engineering`, `iiot`, `database`, `enterprise_architecture`, `manufacturing`, `mind_map`, `computer_science`)
- **Diagrams per Domain:** 11 (10 manually placed + 1 auto-layout)
- **Themes Demonstrated:** 13 (`iiot_dark_gold`, `iiot_light`, `blueprint`, `cyber_slate`, `nord`, `emerald`, `crimson`, `monochrome`, `solarized_light`, `pastel_light`, `dracula`, `synthwave`, `high_contrast`)
- **Theme Variety per Domain:** at least 3 distinct varieties per domain
- **Built-in Domain Vector Icons:** 60 custom open-source SVG vector icons
- **Zero External Dependencies:** 100% Python standard library core engine execution
- **Auto-Layout Examples:** each domain's `11_auto_*.py` uses `Diagram(layout="auto")` — no `.at()` / `.right_of()` calls; the engine derives every position from the edge graph


---

## 1. Cloud Architecture (`examples/cloud/`)

Modern distributed, serverless, hybrid, and multi-region cloud topologies.

| # | Script & Output | Title | Theme | Complexity | Key Components / Icons |
|---|---|---|---|---|---|
| 01 | [`01_simple_vpc_web.py`](cloud/01_simple_vpc_web.py) | Simple VPC Web Application | `nord` | Simple | ALB, Web Servers, Multi-AZ PostgreSQL |
| 02 | [`02_serverless_event_pipeline.py`](cloud/02_serverless_event_pipeline.py) | Serverless Event Pipeline | `cyber_slate` | Moderate | API Gateway, Event Hub, Serverless Functions, S3 |
| 03 | [`03_cdn_multi_region_edge.py`](cloud/03_cdn_multi_region_edge.py) | CDN & Multi-Region Edge Topology | `blueprint` | Advanced | Anycast DNS, Global CDN Edge, Region Primary & Secondary |
| 04 | [`04_hybrid_cloud_vpn.py`](cloud/04_hybrid_cloud_vpn.py) | Hybrid Cloud VPN Architecture | `iiot_dark_gold` | Moderate | Customer Gateway, IPSec VPN, VPC Ingress, File Storage |
| 05 | [`05_microservices_service_mesh.py`](cloud/05_microservices_service_mesh.py) | Microservices Service Mesh | `emerald` | Advanced | Ingress Controller, Auth, Orders, Payments, Mesh Control |
| 06 | [`06_multi_cloud_dr_failover.py`](cloud/06_multi_cloud_dr_failover.py) | Multi-Cloud Disaster Recovery | `crimson` | Enterprise | Global DNS Traffic, AWS Primary VPC, Azure Secondary VNet |
| 07 | [`07_data_lakehouse_ingest.py`](cloud/07_data_lakehouse_ingest.py) | Cloud Data Lakehouse Ingestion | `monochrome` | Advanced | Kafka Streaming, Ingest Workers, Bronze/Silver/Gold Lakehouse |
| 08 | [`08_zero_trust_ingress_security.py`](cloud/08_zero_trust_ingress_security.py) | Zero Trust Ingress Security Stack | `cyber_slate` | Enterprise | WAF/DDoS Shield, Mutual TLS Gateway, IdP, Internal Apps |
| 09 | [`09_iot_cloud_fleet_management.py`](cloud/09_iot_cloud_fleet_management.py) | Global IoT Cloud Fleet Management | `nord` | Advanced | Edge Gateways, MQTT Ingestion Broker, TimeSeries DB, Telemetry |
| 10 | [`10_global_enterprise_backbone.py`](cloud/10_global_enterprise_backbone.py) | Global Cloud Enterprise Backbone | `iiot_dark_gold` | Enterprise | Cloud WAN Hub, Direct Connect, Enterprise VPCs, Multi-Region Transit |
| 11 | [`11_auto_serverless_pipeline.py`](cloud/11_auto_serverless_pipeline.py) | Auto-Laid-Out Serverless Pipeline | `nord` | Moderate (auto-layout) | Client, API Gateway, Order/Billing Functions, Event Queue, Orders DB |

---

## 2. Artificial Intelligence & Machine Learning (`examples/ai/`)

Large language model pipelines, autonomous agent swarms, vector retrieval, distributed training clusters, and robotics SLAM architectures.

| # | Script & Output | Title | Theme | Complexity | Key Components / Icons |
|---|---|---|---|---|---|
| 01 | [`01_simple_rag_pipeline.py`](ai/01_simple_rag_pipeline.py) | Simple Retrieval-Augmented Generation (RAG) | `nord` | Moderate | Embedding Model, Vector DB (HNSW), Foundation LLM |
| 02 | [`02_multimodal_vision_inference.py`](ai/02_multimodal_vision_inference.py) | Multimodal Vision Inference Service | `cyber_slate` | Moderate | Camera Stream, Preprocessing, Vision-Language Model, Detection Cache |
| 03 | [`03_agentic_tool_orchestration.py`](ai/03_agentic_tool_orchestration.py) | Agentic Tool-Use Orchestration Framework | `emerald` | Advanced | Supervisor Agent, Search Tool, Code Sandbox, SQL Tool, Memory Store |
| 04 | [`04_distributed_training_cluster.py`](ai/04_distributed_training_cluster.py) | Distributed LLM Training Cluster | `crimson` | Enterprise | Master Coordinator, Multi-GPU Worker Nodes, High-Speed NVLink/InfiniBand Fabric |
| 05 | [`05_feature_store_mlops.py`](ai/05_feature_store_mlops.py) | Enterprise Feature Store & MLOps Pipeline | `blueprint` | Advanced | Batch & Stream Ingest, Online Redis, Offline Parquet, Model Registry |
| 06 | [`06_fine_tuning_lora_pipeline.py`](ai/06_fine_tuning_lora_pipeline.py) | Parameter-Efficient Fine-Tuning (LoRA) Pipeline | `nord` | Moderate | Curated Dataset, Frozen Base LLM, LoRA Adapter Weights, Evaluation Harness |
| 07 | [`07_enterprise_knowledge_graph_llm.py`](ai/07_enterprise_knowledge_graph_llm.py) | Enterprise GraphRAG Knowledge Architecture | `iiot_dark_gold` | Advanced | Triplet Extractor, Entity Graph Store, Hybrid Vector/Graph Retriever, LLM |
| 08 | [`08_ai_guardrails_safety_eval.py`](ai/08_ai_guardrails_safety_eval.py) | AI Safety & Alignment Guardrail Filter | `cyber_slate` | Moderate | Prompt Injection Filter, PII Masking, LLM Core, Hallucination Scorer |
| 09 | [`09_autonomous_robotics_slam.py`](ai/09_autonomous_robotics_slam.py) | Autonomous Mobile Robot SLAM & Perception Stack | `emerald` | Enterprise | LiDAR & Stereo Depth, Visual Odometry, EKF State Estimator, Costmap Planner |
| 10 | [`10_self_hosted_vllm_cluster.py`](ai/10_self_hosted_vllm_cluster.py) | High-Throughput vLLM Serving Cluster | `monochrome` | Advanced | Reverse Proxy Router, PagedAttention vLLM Workers, Model Storage Cache |
| 11 | [`11_auto_training_pipeline.py`](ai/11_auto_training_pipeline.py) | Auto-Laid-Out Training Pipeline | `dracula` | Moderate (auto-layout) | Raw Lake, Feature Store, Trainer, Experiment Tracker, Model Registry, Inference API |

---

## 3. Computer & Edge Systems (`examples/computer/`)

Workstations, home labs, embedded RTOS, industrial PLCs, edge gateways, and developer environments.

| # | Script & Output | Title | Theme | Complexity | Key Components / Icons |
|---|---|---|---|---|---|
| 01 | [`01_workstation_peripherals.py`](computer/01_workstation_peripherals.py) | Developer Workstation & Peripheral Bus | `nord` | Simple | Host Tower, Thunderbolt Dock, Dual Displays, NVMe External |
| 02 | [`02_home_lab_network.py`](computer/02_home_lab_network.py) | Home Lab Server Topology | `blueprint` | Moderate | Core Router/Firewall, Managed PoE Switch, Proxmox Hypervisor, TrueNAS |
| 03 | [`03_plc_industrial_io.py`](computer/03_plc_industrial_io.py) | Industrial PLC & Remote I/O Bus | `iiot_dark_gold` | Moderate | Allen-Bradley/Siemens PLC, Remote I/O Racks, Modbus RTU Sensor Array |
| 04 | [`04_dual_homed_edge_gateway.py`](computer/04_dual_homed_edge_gateway.py) | Dual-Homed Industrial Edge Gateway | `cyber_slate` | Advanced | OT Industrial Subnet, Edge Gateway Appliance, IT Corporate Network |
| 05 | [`05_developer_terminal_environment.py`](computer/05_developer_terminal_environment.py) | Modern Developer Terminal & Tooling Stack | `monochrome` | Simple | Terminal Emulator, Multiplexer, Neovim/LSP, Container Runtime |
| 06 | [`06_mobile_client_sync.py`](computer/06_mobile_client_sync.py) | Mobile Device Edge Synchronization | `emerald` | Moderate | iOS/Android Clients, Local SQLite/WatermelonDB, Sync Gateway, Cloud Datastore |
| 07 | [`07_embedded_rtos_system.py`](computer/07_embedded_rtos_system.py) | Real-Time Embedded Microcontroller Architecture | `nord` | Advanced | ARM Cortex-M7, FreeRTOS Scheduler, Sensor Tasks, CAN-FD Transceiver |
| 08 | [`08_vdi_thin_client_fleet.py`](computer/08_vdi_thin_client_fleet.py) | Enterprise Virtual Desktop (VDI) Thin Client Fleet | `blueprint` | Enterprise | Thin Client Terminals, Secure Gateway, VDI Connection Broker, Hyper-V Host |
| 09 | [`09_scada_hmi_control_station.py`](computer/09_scada_hmi_control_station.py) | SCADA Supervisory HMI Station | `iiot_dark_gold` | Advanced | Dual HMI Displays, Industrial PC, Redundant SCADA Servers, Plant Network |
| 10 | [`10_high_performance_workstation_storage.py`](computer/10_high_performance_workstation_storage.py) | High-Performance Workstation NVMe Storage Tier | `crimson` | Advanced | Threadripper CPU, PCIe Gen5 Switch, U.2 NVMe RAID Array, 100GbE NIC |
| 11 | [`11_auto_workstation_stack.py`](computer/11_auto_workstation_stack.py) | Auto-Laid-Out Workstation Stack | `solarized_light` | Simple (auto-layout) | Applications, Runtime, Kernel, Drivers, Hardware |

---

## 4. Datacenter Infrastructure (`examples/datacenter/`)

High-density compute pods, SAN fabrics, leaf-spine network fabrics, power distribution, and concurrently maintainable Tier IV designs.

| # | Script & Output | Title | Theme | Complexity | Key Components / Icons |
|---|---|---|---|---|---|
| 01 | [`01_single_rack_blade_chassis.py`](datacenter/01_single_rack_blade_chassis.py) | 42U Server Rack & Blade Chassis | `blueprint` | Moderate | Top-of-Rack (ToR) Switch, Dual PDUs, Blade Enclosure, Storage Shelves |
| 02 | [`02_san_storage_fabric.py`](datacenter/02_san_storage_fabric.py) | Fibre Channel Storage Area Network (SAN) | `nord` | Advanced | Compute Hosts, Fabric A Brocade Switch, Fabric B Brocade Switch, All-Flash Array |
| 03 | [`03_leaf_spine_clos_network.py`](datacenter/03_leaf_spine_clos_network.py) | Leaf-Spine Clos Network Fabric | `cyber_slate` | Enterprise | Spine Switches 01-04, Leaf Switches 01-04, Server Racks with EVPN-VXLAN |
| 04 | [`04_power_distribution_ups.py`](datacenter/04_power_distribution_ups.py) | Datacenter 2N Power Distribution & UPS | `crimson` | Enterprise | Utility Feed, Diesel Generator, Dual Rotary UPS A/B, STS, Floor PDUs |
| 05 | [`05_hvac_containment_cooling.py`](datacenter/05_hvac_containment_cooling.py) | Hot/Cold Aisle Containment & CRAC Units | `emerald` | Moderate | Chilled Water Chiller, CRAC Units A & B, Cold Aisle Plenum, Server Inlets |
| 06 | [`06_kubernetes_bare_metal.py`](datacenter/06_kubernetes_bare_metal.py) | Bare-Metal Kubernetes Infrastructure Pod | `nord` | Advanced | Control Plane Nodes (etcd), Calico BGP ToR Switch, Worker Compute Nodes |
| 07 | [`07_disaster_recovery_datacenter_pair.py`](datacenter/07_disaster_recovery_datacenter_pair.py) | Active-Active Datacenter Replication Pair | `blueprint` | Enterprise | Primary Metro DC, Secondary Remote DC, Dark Fiber DCI, Storage Replication |
| 08 | [`08_high_density_ai_compute_pod.py`](datacenter/08_high_density_ai_compute_pod.py) | High-Density AI GPU SuperPOD Architecture | `iiot_dark_gold` | Enterprise | In-Row Liquid Cooling CDU, 8x NVIDIA HGX Nodes, Quantum InfiniBand Fabric |
| 09 | [`09_edge_micro_datacenter.py`](datacenter/09_edge_micro_datacenter.py) | Ruggedized Edge Micro-Datacenter (MDC) | `cyber_slate` | Moderate | NEMA-4 Enclosure, Edge Converged Host, Integrated Lithium UPS, LTE Failover |
| 10 | [`10_tier4_concurrently_maintainable.py`](datacenter/10_tier4_concurrently_maintainable.py) | Tier IV Concurrently Maintainable Datacenter | `monochrome` | Enterprise | Dual Substation Feeds, Independent Power Paths A/B, Isolated Cooling Loops |
| 11 | [`11_auto_spine_leaf.py`](datacenter/11_auto_spine_leaf.py) | Auto-Laid-Out Spine-Leaf Fabric | `blueprint` | Moderate (auto-layout) | Spine 1-2, Leaf 1-3, Rack A-C |

---

## 5. Business Processes & Operational Workflows (`examples/business_process/`)

Cross-functional enterprise workflows, approval gates, compliance audits, procurement, and automated fraud triage.

| # | Script & Output | Title | Theme | Complexity | Key Components / Icons |
|---|---|---|---|---|---|
| 01 | [`01_order_to_cash.py`](business_process/01_order_to_cash.py) | Order-to-Cash (O2C) Enterprise Workflow | `emerald` | Moderate | Customer Ingestion, Credit Check Gate, ERP Inventory Allocation, Invoicing |
| 02 | [`02_employee_onboarding.py`](business_process/02_employee_onboarding.py) | Enterprise Employee Onboarding Lifecycle | `nord` | Moderate | Offer Acceptance, HR Record Creation, IT Identity Provisioning, Day One Induction |
| 03 | [`03_it_incident_escalation.py`](business_process/03_it_incident_escalation.py) | IT Major Incident Escalation & Response | `crimson` | Advanced | Alert Ingestion, Tier 1 Triage, Incident Commander War Room, RCA Post-Mortem |
| 04 | [`04_procure_to_pay.py`](business_process/04_procure_to_pay.py) | Procure-to-Pay (P2P) Purchasing Process | `blueprint` | Advanced | Requisition Submission, VP Budget Approval, Vendor PO Issuance, 3-Way Match |
| 05 | [`05_regulatory_compliance_audit.py`](business_process/05_regulatory_compliance_audit.py) | SOC 2 / ISO 27001 Compliance Audit Workflow | `iiot_dark_gold` | Advanced | Control Evidence Collection, Auditor Sampling Review, Remediation Ticket, Report |
| 06 | [`06_software_release_gate.py`](business_process/06_software_release_gate.py) | Automated Production Software Release Gate | `cyber_slate` | Moderate | Commit Tagging, Static Security Analysis (SAST), Canary Deploy, Rollback Gate |
| 07 | [`07_customer_loan_origination.py`](business_process/07_customer_loan_origination.py) | Customer Loan Origination & Underwriting | `emerald` | Enterprise | Online Application, Automated Credit Scoring Engine, Underwriter Review, Disbursement |
| 08 | [`08_supply_chain_rfq_fulfillment.py`](business_process/08_supply_chain_rfq_fulfillment.py) | Supply Chain RFQ & Supplier Selection | `blueprint` | Advanced | Bill of Materials Intake, Vendor Bidding Portal, Cost/Lead-Time Matrix, Contract Award |
| 09 | [`09_claims_processing_fraud_detection.py`](business_process/09_claims_processing_fraud_detection.py) | Insurance Claims Triage & Fraud Detection | `crimson` | Enterprise | FNOL Filing, ML Fraud Score Model, Special Investigation Unit (SIU), Fast-Track Pay |
| 10 | [`10_enterprise_change_management.py`](business_process/10_enterprise_change_management.py) | Enterprise ITIL Change Advisory Board (CAB) | `monochrome` | Advanced | Change Request (RFC), Risk Assessment Matrix, CAB Review Meeting, Scheduled Maintenance |
| 11 | [`11_auto_order_to_cash.py`](business_process/11_auto_order_to_cash.py) | Auto-Laid-Out Order to Cash | `pastel_light` | Moderate (auto-layout) | Order Received, Credit Check, Fulfil Order, Invoice, Payment Received, Collections |

---

## 6. Cybersecurity Architecture (`examples/cybersecurity/`)

Threat hunting, Zero Trust access, SIEM/SOAR telemetry, PKI trust hierarchy, secrets management, and air-gapped recovery vaults.

| # | Script & Output | Title | Theme | Complexity | Key Components / Icons |
|---|---|---|---|---|---|
| 01 | [`01_perimeter_defense_dmz.py`](cybersecurity/01_perimeter_defense_dmz.py) | Enterprise DMZ Perimeter Defense | `crimson` | Moderate | Web Client, External Firewall, Reverse Proxy, WAF Inspector, Internal mTLS |
| 02 | [`02_soc_siem_pipeline.py`](cybersecurity/02_soc_siem_pipeline.py) | SOC & SIEM Telemetry Analytics Pipeline | `cyber_slate` | Advanced | EDR Fleet, Firewall Syslog, CloudTrail, Log Aggregator, SIEM ML, SOAR |
| 03 | [`03_zero_trust_ztna.py`](cybersecurity/03_zero_trust_ztna.py) | Zero Trust Network Access (ZTNA) Architecture | `nord` | Advanced | Remote Employee, Device Posture Agent, Enterprise IdP, ZTNA Policy Broker, App Gateway |
| 04 | [`04_pki_ca_hierarchy.py`](cybersecurity/04_pki_ca_hierarchy.py) | Public Key Infrastructure (PKI) Certificate Hierarchy | `blueprint` | Advanced | Offline Root CA (HSM), TLS Issuing CA, Code Signing CA, OCSP Responder, End Entities |
| 05 | [`05_edr_threat_hunting.py`](cybersecurity/05_edr_threat_hunting.py) | Endpoint Detection & Threat Hunting Grid | `crimson` | Advanced | Managed OS Endpoints, Telemetry Ingestion Hub, ATT&CK Correlator, SOC Lead, Host Isolation |
| 06 | [`06_secrets_vault_rotation.py`](cybersecurity/06_secrets_vault_rotation.py) | Automated Secrets Vault & Credential Rotation | `emerald` | Advanced | Kubernetes Pod, HashiCorp Vault, FIPS HSM Core, Rotation Controller, Postgres |
| 07 | [`07_honeynet_deception_grid.py`](cybersecurity/07_honeynet_deception_grid.py) | Deception Technology Honeynet Grid | `cyber_slate` | Advanced | Adversary Terminal, Decoy SSH Bastion, Decoy Admin Portal, Honeytoken DB, BGP Sinkhole |
| 08 | [`08_ids_ips_inline_inspection.py`](cybersecurity/08_ids_ips_inline_inspection.py) | Inline IDS/IPS Deep Packet Inspection | `iiot_dark_gold` | Enterprise | Border Router, Network Packet Broker TAP, ASIC SSL Decryptor, Suricata IPS, Core Switch |
| 09 | [`09_iam_federation_saml_oidc.py`](cybersecurity/09_iam_federation_saml_oidc.py) | Enterprise IAM Federation & SSO Pipeline | `monochrome` | Moderate | Corporate User, FIDO2 WebAuthn Key, Okta/Entra IdP, LDAP/AD, SaaS App, OIDC Portal |
| 10 | [`10_ransomware_containment_airgap.py`](cybersecurity/10_ransomware_containment_airgap.py) | Ransomware Defense & Optical Air-Gapped Vault | `crimson` | Enterprise | Production SAN, Backup Master, Optical Data Diode (Tx-Only), Immutable WORM Vault, Cleanroom Sandbox |
| 11 | [`11_auto_soc_pipeline.py`](cybersecurity/11_auto_soc_pipeline.py) | Auto-Laid-Out SOC Detection Pipeline | `cyber_slate` | Moderate (auto-layout) | Endpoints, Firewalls, Log Collector, Correlation Engine, SOAR, Analyst Console |

---

## 7. Network Engineering (`examples/network_engineering/`)

Campus LAN switching, multihomed BGP peering, provider MPLS L3VPN, EVPN-VXLAN datacenter fabrics, SD-WAN, and DWDM optical transport.

| # | Script & Output | Title | Theme | Complexity | Key Components / Icons |
|---|---|---|---|---|---|
| 01 | [`01_three_tier_campus_lan.py`](network_engineering/01_three_tier_campus_lan.py) | Three-Tier Hierarchical Campus LAN | `blueprint` | Moderate | Core Switch Pair, Distribution Switch Pair, Floor Access Switches (PoE++) |
| 02 | [`02_bgp_dual_multihomed_wan.py`](network_engineering/02_bgp_dual_multihomed_wan.py) | Dual-Homed eBGP Enterprise WAN Peering | `cyber_slate` | Advanced | Tier-1 Transit ISPs (AS 174, AS 2914), Edge Core Routers, iBGP Full Mesh, Core Fabric |
| 03 | [`03_mpls_vpn_backbone.py`](network_engineering/03_mpls_vpn_backbone.py) | MPLS Layer 3 VPN Service Provider Backbone | `iiot_dark_gold` | Enterprise | Customer Edge (CE) Routers, Provider Edge (PE) Routers, 400G P Core LSRs, VRF Segmentation |
| 04 | [`04_vxlan_evpn_datacenter_fabric.py`](network_engineering/04_vxlan_evpn_datacenter_fabric.py) | EVPN-VXLAN Datacenter Spine-Leaf Fabric | `nord` | Enterprise | 400G Spine Switches, Leaf VTEP Switches, MLAG Server Dual-Homing, VXLAN VNIs |
| 05 | [`05_sd_wan_hub_and_spoke.py`](network_engineering/05_sd_wan_hub_and_spoke.py) | Enterprise SD-WAN Hub-and-Spoke Topology | `emerald` | Advanced | vManage Orchestrator, vSmart OMP Controller, HQ Hub Router, Branch Office Appliances |
| 06 | [`06_ha_firewall_cluster_carp_sync.py`](network_engineering/06_ha_firewall_cluster_carp_sync.py) | High-Availability Active/Passive Firewall Cluster | `crimson` | Advanced | WAN Switch (CARP VIP), Active/Passive Firewall Pair, Dedicated pfsync Heartbeat, LAN Switch |
| 07 | [`07_dwdm_metro_optical_ring.py`](network_engineering/07_dwdm_metro_optical_ring.py) | Metro DWDM Optical Transport Ring | `blueprint` | Enterprise | Metro West/East/South ROADMs (96 Waves), 144F Optical Patch Bay, 100G Muxponder |
| 08 | [`08_ospf_multi_area_enterprise.py`](network_engineering/08_ospf_multi_area_enterprise.py) | OSPF Multi-Area Enterprise Routing | `monochrome` | Advanced | Area 0 Backbone Core Routers, Area 10 Campus ABR, Datacenter ASBR, BGP Redistribution |
| 09 | [`09_radius_802_1x_nac.py`](network_engineering/09_radius_802_1x_nac.py) | 802.1X Network Access Control (NAC) & RADIUS | `nord` | Moderate | Supplicant Laptop, 802.1X Authenticator Switch, FreeRADIUS/ISE, Active Directory, Dynamic VLANs |
| 10 | [`10_dns_anycast_authoritative_mesh.py`](network_engineering/10_dns_anycast_authoritative_mesh.py) | Global Anycast Authoritative DNS Network | `cyber_slate` | Enterprise | Global DNS Clients, US-East & EU-Central BGP Anycast PoPs, Knot/BIND Resolvers, Master Zone DB |
| 11 | [`11_auto_campus_core.py`](network_engineering/11_auto_campus_core.py) | Auto-Laid-Out Campus Core | `emerald` | Moderate (auto-layout) | Internet, Edge Router, Core Switch, Distribution A/B, Access A/B |

---

## 8. Industrial IoT & Automation (`examples/iiot/`)

Edge-to-cloud UNS architectures, high-availability broker clusters, Sparkplug B pipelines, predictive maintenance, redundant SCADA, and AGV fleet telemetry.

| # | Script & Output | Title | Theme | Complexity | Key Components / Icons |
|---|---|---|---|---|---|
| 01 | [`01_baltimore_plant_to_cloud.py`](iiot/01_baltimore_plant_to_cloud.py) | Baltimore Plant to Managed Cloud | `iiot_dark_gold` | Moderate | Siemens S7 PLC, IIoT Edge Gateway, Central MQTT Broker, Grafana Dashboard |
| 02 | [`02_high_availability_broker.py`](iiot/02_high_availability_broker.py) | High Availability Broker Cluster | `iiot_dark_gold` | Advanced | Load Balancer VIP, 3-Node Active MQTT Cluster, Clustered Storage |
| 03 | [`03_sparkplug_b_pipeline.py`](iiot/03_sparkplug_b_pipeline.py) | Sparkplug B Unified Namespace | `iiot_dark_gold` | Advanced | Sensors & PLCs, Sparkplug B Edge Node, UNS Central Broker, Host SCADA |
| 04 | [`04_predictive_maintenance_vibration.py`](iiot/04_predictive_maintenance_vibration.py) | Predictive Maintenance Vibration Analysis | `blueprint` | Moderate | 3-Axis Accelerometer, Bearing Thermocouple, DSP Anomaly Detector, Historian |
| 05 | [`05_scada_historian_redundancy.py`](iiot/05_scada_historian_redundancy.py) | SCADA & Historian Dual Redundancy | `iiot_light` | Enterprise | Redundant Plant PLC, Active/Standby SCADA Pair, Replicated Historian Archive |
| 06 | [`06_opc_ua_edge_aggregation.py`](iiot/06_opc_ua_edge_aggregation.py) | OPC UA TSN Edge Aggregator | `cyber_slate` | Advanced | Multi-Vendor PLCs, Robot Controller, OPC UA Aggregator, Enterprise MES |
| 07 | [`07_smart_factory_mes_integration.py`](iiot/07_smart_factory_mes_integration.py) | Smart Factory MES & ERP Integration | `emerald` | Enterprise | Line Operator HMI, Pallet RFID Scanner, IPC Controller, Core MES, SAP ERP |
| 08 | [`08_automated_guided_vehicle_fleet.py`](iiot/08_automated_guided_vehicle_fleet.py) | AGV Fleet Telemetry & Traffic Management | `nord` | Advanced | AGV Forklift & Tugger Units, Industrial Wi-Fi Mesh, Fleet Traffic Manager |
| 09 | [`09_cold_chain_environmental_telemetry.py`](iiot/09_cold_chain_environmental_telemetry.py) | Cold Chain Environmental Monitoring | `nord` | Moderate | Freezer & Chiller Probes, LoRaWAN Gateway, 21 CFR Part 11 Audit Datastore |
| 10 | [`10_water_wastewater_remote_rtu.py`](iiot/10_water_wastewater_remote_rtu.py) | Water & Wastewater Remote RTU Mesh | `blueprint` | Advanced | Submersible Level Sensors, Solar-Powered RTU, Cellular LTE-M, Central SCADA |
| 11 | [`11_auto_uns_backbone.py`](iiot/11_auto_uns_backbone.py) | Auto-Laid-Out UNS Backbone | `iiot_dark_gold` | Moderate (auto-layout) | PLC, Sensor Array, Edge Gateway, MQTT Broker, Historian, Dashboard |

---

## 9. Databases (`examples/database/`)

Schemas, replication, sharding, change data capture, lakehouse pipelines, storage-engine internals and backup strategy.

| # | Script & Output | Title | Theme | Complexity | Key Components / Icons |
|---|---|---|---|---|---|
| 01 | [`01_entity_relationship_model.py`](database/01_entity_relationship_model.py) | Online Store Entity-Relationship Model | `iiot_light` | Simple | 5 tables with typed columns, PK/FK/UQ markers, cardinality at each end |
| 02 | [`02_star_schema_warehouse.py`](database/02_star_schema_warehouse.py) | Retail Sales Star Schema Data Warehouse | `solarized_light` | Moderate | fact_sales with FKs and measures, 5 dimensions, surrogate keys, SCD2 customer dimension |
| 03 | [`03_primary_replica_failover.py`](database/03_primary_replica_failover.py) | PostgreSQL Primary/Replica Replication with Automatic Failover | `nord` | Moderate | HAProxy/PgBouncer, primary, sync standby, async and cascading replicas, Patroni + etcd |
| 04 | [`04_sharded_cluster.py`](database/04_sharded_cluster.py) | Range-Sharded Document Database Cluster | `blueprint` | Advanced | mongos routers, config server replica set, 3 range shards, balancer |
| 05 | [`05_cdc_pipeline.py`](database/05_cdc_pipeline.py) | Change Data Capture Pipeline from WAL to Kafka | `dracula` | Advanced | WAL + replication slot, Debezium, Schema Registry, topics, DLQ, 4 sink connectors |
| 06 | [`06_lakehouse_medallion.py`](database/06_lakehouse_medallion.py) | Lakehouse Medallion Architecture, Bronze to Gold | `emerald` | Enterprise | Streaming/CDC/batch ingest, bronze/silver/gold, BI/ML/reverse-ETL, catalog, DQ, orchestrator |
| 07 | [`07_btree_index_pages.py`](database/07_btree_index_pages.py) | B+-Tree Index Page Structure | `paper` | Advanced | Root and leaf pages, sibling chain, 8 KiB slotted page layout, height formula, caption |
| 08 | [`08_lsm_tree_compaction.py`](database/08_lsm_tree_compaction.py) | LSM-Tree Levelled Compaction | `paper` | Advanced | WAL and memtable, flush, L0–L3 on one key axis, compaction, write-amplification formula |
| 09 | [`09_query_plan_tree.py`](database/09_query_plan_tree.py) | Physical Query Plan Tree for a Join and Top-N | `paper` | Moderate | Limit/Sort/Aggregate/Hash Join/scans tree, row estimates, SQL, cost math, caption |
| 10 | [`10_backup_pitr_strategy.py`](database/10_backup_pitr_strategy.py) | Backup and Point-in-Time Recovery Strategy | `cyber_slate` | Enterprise | WAL archive, full/differential backups, KMS + object lock, cross-region copy, restore tests, PITR timeline with RPO/RTO |
| 11 | [`11_auto_cache_aside_read_path.py`](database/11_auto_cache_aside_read_path.py) | Auto-Laid-Out Cache-Aside Read and Write Path | `pastel_light` | Simple (auto-layout) | Hit/miss decision, read replica, WAL stream, CDC cache invalidation |

---

## 10. Enterprise Architecture (`examples/enterprise_architecture/`)

Structure, portfolio and layered views: C4, ArchiMate, capability and value-stream maps, portfolio rationalisation, transition roadmaps, integration, data governance and landing zones.

| # | Script & Output | Title | Theme | Complexity | Key Components / Icons |
|---|---|---|---|---|---|
| 01 | [`01_c4_system_context.py`](enterprise_architecture/01_c4_system_context.py) | C4 System Context: Retail Internet Banking | `pastel_light` | Simple | Customers and staff, Internet Banking System, Core Banking Mainframe, external e-mail, credit bureau, open-banking directory |
| 02 | [`02_business_capability_map.py`](enterprise_architecture/02_business_capability_map.py) | Insurance Business Capability Map with Maturity Heatmap | `iiot_light` | Moderate | L1 domains, L2 groups, L3 capabilities shaded by maturity, shared enablers, legend |
| 03 | [`03_application_portfolio_time.py`](enterprise_architecture/03_application_portfolio_time.py) | Application Portfolio Rationalisation (TIME Model) | `solarized_light` | Moderate | Tolerate/Invest/Migrate/Eliminate quadrants, migration arrows, cost and owner metadata |
| 04 | [`04_c4_container_view.py`](enterprise_architecture/04_c4_container_view.py) | C4 Container View: Internet Banking System | `nord` | Moderate | SPA, mobile app, API gateway, services with own databases, Kafka bus, notification worker |
| 05 | [`05_archimate_layered_view.py`](enterprise_architecture/05_archimate_layered_view.py) | ArchiMate Layered View: Insurance Claims Handling | `paper` | Advanced | Business/application/technology bands, serving vs realisation relations, caption |
| 06 | [`06_integration_architecture.py`](enterprise_architecture/06_integration_architecture.py) | Enterprise Integration Architecture: API, Event and ESB Patterns | `blueprint` | Advanced | API gateway + OAuth, iPaaS, event streaming, legacy ESB, managed file transfer, systems of record |
| 07 | [`07_value_stream_capability_map.py`](enterprise_architecture/07_value_stream_capability_map.py) | Value Stream to Capability Cross-Map: Acquire a Home Loan | `monochrome` | Advanced | Chevron stages, L2 capabilities per stage, dashed capability gaps, legend |
| 08 | [`08_transition_roadmap.py`](enterprise_architecture/08_transition_roadmap.py) | Core Systems Transition Roadmap: Baseline to Target | `paper` | Advanced | Baseline, two plateaus and target across 4 lanes, work packages with budgets, caption |
| 09 | [`09_data_governance_mdm.py`](enterprise_architecture/09_data_governance_mdm.py) | Enterprise Data Governance and Master Data Management | `emerald` | Advanced | CDO, council, stewards, match & merge, golden records, DQ rules, catalogue |
| 10 | [`10_cloud_landing_zone_operating_model.py`](enterprise_architecture/10_cloud_landing_zone_operating_model.py) | Multi-Business-Unit Cloud Landing Zone and Operating Model | `cyber_slate` | Enterprise | CCoE, account vending, FinOps, OUs, identity federation, Direct Connect |
| 11 | [`11_auto_application_landscape.py`](enterprise_architecture/11_auto_application_landscape.py) | Auto-Laid-Out Retail Application Landscape | `dracula` | Simple (auto-layout) | Web shop and POS → API gateway → OMS and CRM → ERP and WMS → data platform |

---

## 11. Manufacturing & Semiconductor (`examples/manufacturing/`)

Process, production and control: six semiconductor fab diagrams (front-end loop, lithography, fab automation, run-to-run control, yield, back-end assembly and test) and five general manufacturing ones (ISA-95, automotive plant, OEE, SPC, ISA-88).

| # | Script & Output | Title | Theme | Complexity | Key Components / Icons |
|---|---|---|---|---|---|
| 01 | [`01_wafer_fab_process_loop.py`](manufacturing/01_wafer_fab_process_loop.py) | Front-End Wafer Fab Re-entrant Process Loop | `paper` | Advanced | Deposit, coat, expose, develop, etch, strip with wafer cross-sections; return loop through clean, metrology, implant + anneal, CMP |
| 02 | [`02_lithography_cell.py`](manufacturing/02_lithography_cell.py) | Lithography Cell with Overlay & CD Feedback | `blueprint` | Moderate | Coater/developer track, scanner stages, reticle stocker, CD-SEM, overlay metrology, run-to-run controller, MES |
| 03 | [`03_fab_automation_stack.py`](manufacturing/03_fab_automation_stack.py) | 300 mm Fab Automation: MES to AMHS to Tool | `nord` | Advanced | MES + dispatcher, MCS, EAP, FDC, FOUP stocker, OHT, load port (E84/E87), EFEM, SECS/GEM and EDA links |
| 04 | [`04_apc_run_to_run_fdc.py`](manufacturing/04_apc_run_to_run_fdc.py) | Run-to-Run Control with Fault Detection | `paper` | Advanced | EWMA run-to-run equations, drifting tool model, metrology feedback, FDC T² hold |
| 05 | [`05_yield_management.py`](manufacturing/05_yield_management.py) | Semiconductor Yield Management Data Flow | `cyber_slate` | Advanced | Inline metrology, inspection, SEM review + ADC, e-test, wafer sort, yield warehouse, commonality analytics, MES hold |
| 06 | [`06_backend_assembly_test.py`](manufacturing/06_backend_assembly_test.py) | Semiconductor Back-End Assembly & Test Line | `solarized_light` | Moderate | Backgrind, dicing, die attach from bin map, wire bond, mold, ball attach, burn-in, final test, tape & reel, FA |
| 07 | [`07_isa95_levels.py`](manufacturing/07_isa95_levels.py) | ISA-95 Functional Hierarchy, Levels 0 to 4 | `iiot_light` | Moderate | Five level bands with time scales; ERP/MES/SCADA/PLC/field devices; B2MML at level 3/4 |
| 08 | [`08_automotive_assembly_line.py`](manufacturing/08_automotive_assembly_line.py) | Automotive Plant Flow: Press, Body, Paint, Assembly | `emerald` | Advanced | Press, body-in-white, body stores, paint, trim, chassis marriage, final line, EOL test, JIS seats |
| 09 | [`09_oee_loss_waterfall.py`](manufacturing/09_oee_loss_waterfall.py) | OEE Loss Waterfall for One Shift | `paper` | Advanced | To-scale loss bars; A, P, Q and OEE = A×P×Q computed from the same inputs |
| 10 | [`10_spc_control_chart_fishbone.py`](manufacturing/10_spc_control_chart_fishbone.py) | SPC X-bar Chart and Ishikawa Root-Cause Diagram | `paper` | Advanced | X-bar chart with computed limits and sigma zones, rule violations detected, 6M fishbone |
| 11 | [`11_auto_isa88_batch_recipe.py`](manufacturing/11_auto_isa88_batch_recipe.py) | Auto-Laid-Out ISA-88 Batch Recipe Hierarchy | `dracula` | Moderate (auto-layout) | General → site → master → control recipe; procedure, unit procedure, operations, phases |

---

## 12. Mind Maps (`examples/mind_map/`)

Planning, study, review and interview mind maps: a central topic, colour-coded curved branches and nodes that shrink with depth. No icons; they show `Style`, curved routing and computed radial positions.

| # | Script & Output | Title | Theme | Complexity | Key Components / Icons |
|---|---|---|---|---|---|
| 01 | [`01_product_launch_plan.py`](mind_map/01_product_launch_plan.py) | Product Launch Plan Mind Map | `pastel_light` | Simple | Central pill, 4 colour-coded branches balanced left/right, curved branch lines, sub-topic pills |
| 02 | [`02_startup_idea_brainstorm.py`](mind_map/02_startup_idea_brainstorm.py) | Startup Idea Brainstorm Radial Mind Map | `nord` | Moderate | Radial layout computed with cos/sin, 6 branches (problem, solution, customers, revenue, competition, risks) |
| 03 | [`03_operating_systems_study_notes.py`](mind_map/03_operating_systems_study_notes.py) | Operating Systems Concepts Study Notes | `solarized_light` | Moderate | 6 chapter branches, 18 sub-topics, three node sizes by depth |
| 04 | [`04_meeting_notes_action_items.py`](mind_map/04_meeting_notes_action_items.py) | Sprint 42 Planning Meeting Notes | `emerald` | Simple | Attendees, open questions, decisions, owner-tagged action items |
| 05 | [`05_personal_goals_okrs.py`](mind_map/05_personal_goals_okrs.py) | Personal Goals and OKRs Mind Map | `iiot_light` | Simple | Objectives as branches, key results as leaves, fill shade from % progress, double border when complete |
| 06 | [`06_project_risk_register.py`](mind_map/06_project_risk_register.py) | Data Platform Migration Risk Register | `cyber_slate` | Moderate | Radial, 6 risk categories, 14 risks, fill = severity, severity legend |
| 07 | [`07_book_summary.py`](mind_map/07_book_summary.py) | Book Summary: Designing Data-Intensive Applications | `monochrome` | Moderate | Part, chapter and one-line takeaway levels in grey shades |
| 08 | [`08_incident_retrospective_five_whys.py`](mind_map/08_incident_retrospective_five_whys.py) | Checkout Outage Incident Retrospective | `crimson` | Advanced | Timeline, contributing factors, actions; 5-whys chain ending in the root cause |
| 09 | [`09_system_design_interview.py`](mind_map/09_system_design_interview.py) | System Design Interview: URL Shortener Breakdown | `dracula` | Enterprise | 8 numbered branches, 28 points, sizing notes (QPS, storage, Base62) |
| 10 | [`10_consistency_concept_map.py`](mind_map/10_consistency_concept_map.py) | Distributed Consistency Concept Map | `paper` | Advanced | Paper-figure concept map, linking phrase on every curved arrow, cross-links, caption |
| 11 | [`11_auto_cloud_certification_roadmap.py`](mind_map/11_auto_cloud_certification_roadmap.py) | Auto-Laid-Out Cloud Certification Roadmap | `blueprint` | Moderate (auto-layout) | `layout="auto"` LR topic tree, curved colour-coded branches |

---

## 13. Computer Science (`examples/computer_science/`)

Core computer-science figures in the technical-figure style, with math markup, captions and panels; the algorithms (Dijkstra, subset construction, scheduling, merge sort, Raft commit index) are run in the scripts so the figures show real results.

| # | Script & Output | Title | Theme | Complexity | Key Components / Icons |
|---|---|---|---|---|---|
| 01 | [`01_hash_table_chaining.py`](computer_science/01_hash_table_chaining.py) | Hash table with separate chaining | `solarized_light` | Simple | 7-bucket array, chains with NULL slashes, h(k)=k mod 7, traced search, load factor α, Θ(1+α) |
| 02 | [`02_red_black_tree.py`](computer_science/02_red_black_tree.py) | Red-black tree with NIL leaves | `paper` | Moderate | Valid 10-key red-black tree (asserted), NIL leaves, black-height, h ≤ 2 log₂(n+1) |
| 03 | [`03_merge_sort_recursion.py`](computer_science/03_merge_sort_recursion.py) | Merge sort recursion on eight keys | `paper` | Moderate | Split and merge rows computed by running merge sort, T(n)=2T(n/2)+cn=Θ(n log n) |
| 04 | [`04_dijkstra_shortest_paths.py`](computer_science/04_dijkstra_shortest_paths.py) | Dijkstra shortest paths on a weighted digraph | `paper` | Advanced | 6 vertices, 9 weighted arcs, shortest-path tree, per-step distance table computed with heapq, O((V+E) log V) |
| 05 | [`05_regex_nfa_to_dfa.py`](computer_science/05_regex_nfa_to_dfa.py) | Regular expression to NFA and DFA | `monochrome` | Advanced | NFA for (a\|b)*abb, DFA from a subset construction run in the script, transition table |
| 06 | [`06_cpu_pipeline_hazards.py`](computer_science/06_cpu_pipeline_hazards.py) | Five-stage pipeline with hazards and forwarding | `paper` | Advanced | IF/ID/EX/MEM/WB datapath, hazard and forwarding units, 9-cycle pipeline chart with load-use stall |
| 07 | [`07_virtual_memory_and_caches.py`](computer_science/07_virtual_memory_and_caches.py) | Virtual memory translation and cache hierarchy | `blueprint` | Enterprise | Address fields, TLB, two-level page walk, VIPT split, L1→L2→L3→DRAM latencies, AMAT formula |
| 08 | [`08_tcp_connection_lifecycle.py`](computer_science/08_tcp_connection_lifecycle.py) | TCP connection lifecycle sequence chart | `iiot_light` | Moderate | Lifelines, seq/ack segments, handshake, request/response, 4-segment close, states, RTT and 2·MSL |
| 09 | [`09_cpu_scheduling_gantt.py`](computer_science/09_cpu_scheduling_gantt.py) | CPU scheduling Gantt charts | `pastel_light` | Moderate | FCFS, SRTF and round robin (q=2) simulated in the script, waiting and turnaround averages |
| 10 | [`10_raft_consensus.py`](computer_science/10_raft_consensus.py) | Raft leader election and log replication | `nord` | Enterprise | Follower/Candidate/Leader states, 5 replicated logs coloured by term, AppendEntries, computed commitIndex |
| 11 | [`11_auto_compiler_pass_dag.py`](computer_science/11_auto_compiler_pass_dag.py) | Auto-Laid-Out Compiler Pass DAG | `dracula` | Moderate (auto-layout) | IR → SSA → dominators and alias analysis → inliner, SCCP, GVN, LICM → DCE → instruction selection |

---

## 14. Technical Drawing Primitives (`examples/primitives/`)

Nine focused figures, one per primitive family, all in the `paper` theme. They are separate from the 143 domain diagrams above.

| # | Script & Output | Shows |
|---|---|---|
| 01 | [`01_text_caption_bracket.py`](primitives/01_text_caption_bracket.py) | Free text with markup and math, a caption, curly, square and round brackets |
| 02 | [`02_polygon_polyline_path.py`](primitives/02_polygon_polyline_path.py) | Polygons, a polyline, SVG path data with curves and arcs |
| 03 | [`03_layer_bands.py`](primitives/03_layer_bands.py) | Dashed layer bands with titles and side notes |
| 04 | [`04_nested_and_double_border.py`](primitives/04_nested_and_double_border.py) | Shapes nested three deep, double borders |
| 05 | [`05_edge_weights_and_arrowheads.py`](primitives/05_edge_weights_and_arrowheads.py) | Six arrowhead styles, line weights, a two-way arrow, an ellipsis |
| 06 | [`06_anchors_leaders_splines.py`](primitives/06_anchors_leaders_splines.py) | Fractional anchors, a point endpoint, a shared trunk, leaders, a spline |
| 07 | [`07_projected_solids.py`](primitives/07_projected_solids.py) | Cuboids in oblique and isometric projection, a polyhedron with a cutting plane, a prism |
| 08 | [`08_z_order.py`](primitives/08_z_order.py) | A backdrop under the edges, stacking by `z`, an edge drawn over a box |
| 09 | [`09_align_distribute_units.py`](primitives/09_align_distribute_units.py) | `align()`, `distribute()`, grid snap, lengths in pt and mm |

---

## 15. Technical Figures (`examples/technical/`)

Eleven complete paper-style figures in the `paper` theme, each with a caption. Every one lints clean and has a golden image in `tests/golden/technical/`. The guide is [`docs/technical-figures.md`](../docs/technical-figures.md).

| # | Script & Output | Shows |
|---|---|---|
| 01 | [`01_composition_enforcement.py`](technical/01_composition_enforcement.py) | Four layer bands, shaded panels, a cuboid, a clipped polyhedron, formulas, leaders, a heavy spine: a reproduction of a reference figure |
| 02 | [`02_control_loop.py`](technical/02_control_loop.py) | Feedback control loop with summing junctions, transfer functions and a disturbance |
| 03 | [`03_transformer_block.py`](technical/03_transformer_block.py) | Transformer encoder block with residual connections and tensor shapes |
| 04 | [`04_state_machine.py`](technical/04_state_machine.py) | Connection lifecycle state machine with guards, a self-loop and a final state |
| 05 | [`05_protocol_stack.py`](technical/05_protocol_stack.py) | Two protocol stacks and a router; peer-to-peer and hop-by-hop paths |
| 06 | [`06_memory_layout.py`](technical/06_memory_layout.py) | Process address space with a zoomed stack frame |
| 07 | [`07_timing_diagram.py`](technical/07_timing_diagram.py) | Valid/ready handshake timing diagram with a bus and setup and hold times |
| 08 | [`08_pipeline_equations.py`](technical/08_pipeline_equations.py) | Training pipeline with the equation of each stage and a feedback line |
| 09 | [`09_tensor_shapes.py`](technical/09_tensor_shapes.py) | Tensor shapes through a convolutional network, drawn as solids |
| 10 | [`10_geometric_construction.py`](technical/10_geometric_construction.py) | A geometric construction from computed coordinates |
| 11 | [`11_constraint_region.py`](technical/11_constraint_region.py) | Feasible region, constraints and objective beside a block diagram |

---

## 17. Medical, Engineering and CAD Galleries (`examples/medical/`, `engineering/`, `cad/`)

Thirty paper-style figures, ten per subject, drawn with `diagrams_as_code.draft.Draft` (dimensions, hatching, centerlines, section arrows, GD&T frames, organic outlines) and `Plot`. Values are computed by the scripts. Each lints clean; `tests/test_clinical_engineering_examples.py` checks every script and that the committed SVG matches it. The anatomy is schematic, not diagnostic.

## 16. Textbook Galleries (`examples/calculus_math/`, `differential_equations/`, `physics/`, `finance/`, `logic/`)

Fifty paper-style figures, ten per subject, in the `paper` theme with a caption each. The numbers in them are computed by the scripts (integration, root finding, mean-variance solving, Quine-McCluskey), not typed in. Plots are drawn with `diagrams_as_code.plot.Plot`. Each lints clean; `tests/test_textbook_examples.py` checks every script and that the committed SVG matches it.

### Calculus & Math (`examples/calculus_math/`)

| # | Script | Figure |
|---|--------|--------|
| 01 | [`01_derivative_limit.py`](calculus_math/01_derivative_limit.py) | The derivative as the limit of secant slopes. |
| 02 | [`02_riemann_sums.py`](calculus_math/02_riemann_sums.py) | Left, right and midpoint Riemann sums beside the exact area. |
| 03 | [`03_upper_lower_sums.py`](calculus_math/03_upper_lower_sums.py) | Upper and lower sums squeezing the integral of x^2 on [0, 2]. |
| 04 | [`04_area_between_curves.py`](calculus_math/04_area_between_curves.py) | The area between a parabola and a line. |
| 05 | [`05_taylor_sine.py`](calculus_math/05_taylor_sine.py) | Taylor polynomials of sin x converging. |
| 06 | [`06_epsilon_delta.py`](calculus_math/06_epsilon_delta.py) | The epsilon-delta definition of a limit for f(x) = x^2 at a = 1. |
| 07 | [`07_ivt_mvt.py`](calculus_math/07_ivt_mvt.py) | The Intermediate Value Theorem and the Mean Value Theorem. |
| 08 | [`08_parabola_anatomy.py`](calculus_math/08_parabola_anatomy.py) | The anatomy of a parabola y = a x^2 + b x + c. |
| 09 | [`09_unit_circle.py`](calculus_math/09_unit_circle.py) | Sine, cosine and tangent on the unit circle. |
| 10 | [`10_discriminant.py`](calculus_math/10_discriminant.py) | The three cases of the quadratic discriminant. |

### Differential Equations (`examples/differential_equations/`)

| # | Script | Figure |
|---|--------|--------|
| 01 | [`01_slope_field.py`](differential_equations/01_slope_field.py) | Slope field of y' = x - y with Runge-Kutta solution curves. |
| 02 | [`02_exponential.py`](differential_equations/02_exponential.py) | Exponential growth and decay: y' = k y. |
| 03 | [`03_logistic.py`](differential_equations/03_logistic.py) | Logistic growth y' = r y (1 - y / K) with its equilibria. |
| 04 | [`04_damped_oscillator.py`](differential_equations/04_damped_oscillator.py) | Damped spring-mass oscillator: x'' + 2 zeta w0 x' + w0^2 x = 0. |
| 05 | [`05_saddle.py`](differential_equations/05_saddle.py) | Phase portrait of a saddle: x' = x + 2y, y' = 2x + y. |
| 06 | [`06_stable_spiral.py`](differential_equations/06_stable_spiral.py) | Phase portrait of a stable spiral: x' = -0.25 x + y, y' = -x - 0.25 y. |
| 07 | [`07_center.py`](differential_equations/07_center.py) | Phase portrait of a center: the undamped oscillator x' = v, v' = -w^2 x. |
| 08 | [`08_lotka_volterra.py`](differential_equations/08_lotka_volterra.py) | Lotka-Volterra predator-prey: x' = x (a - b y), y' = y (-c + d x). |
| 09 | [`09_pendulum.py`](differential_equations/09_pendulum.py) | Phase portrait of the pendulum: theta' = w, w' = -sin(theta). |
| 10 | [`10_euler_vs_rk4.py`](differential_equations/10_euler_vs_rk4.py) | Euler against RK4 on y' = y, y(0) = 1, whose exact solution is e^x. |

### Physics (`examples/physics/`)

| # | Script | Figure |
|---|--------|--------|
| 01 | [`01_free_body_incline.py`](physics/01_free_body_incline.py) | Free-body diagram of a block at rest on a rough incline. |
| 02 | [`02_projectile_motion.py`](physics/02_projectile_motion.py) | Projectile motion from a cliff, with the velocity resolved at five instants. |
| 03 | [`03_series_rlc_circuit.py`](physics/03_series_rlc_circuit.py) | A driven series RLC circuit, drawn from circuit symbols built as paths. |
| 04 | [`04_thin_lens_rays.py`](physics/04_thin_lens_rays.py) | Ray diagram for a converging thin lens, with the image found by construction. |
| 05 | [`05_refraction_snell.py`](physics/05_refraction_snell.py) | Refraction at a plane interface: two panels governed by Snell's law. |
| 06 | [`06_standing_waves.py`](physics/06_standing_waves.py) | Standing waves on a string fixed at both ends: the first five harmonics. |
| 07 | [`07_superposition_beats.py`](physics/07_superposition_beats.py) | Superposition of two tones of nearby frequency, and the beats they make. |
| 08 | [`08_carnot_cycle.py`](physics/08_carnot_cycle.py) | The Carnot cycle of an ideal gas on a pressure-volume diagram. |
| 09 | [`09_dipole_field_lines.py`](physics/09_dipole_field_lines.py) | Electric field lines of a dipole, traced numerically. |
| 10 | [`10_hydrogen_energy_levels.py`](physics/10_hydrogen_energy_levels.py) | Energy levels of the hydrogen atom with the Lyman and Balmer transitions. |

### Finance (`examples/finance/`)

| # | Script | Figure |
|---|--------|--------|
| 01 | [`01_candlestick_chart.py`](finance/01_candlestick_chart.py) | Candlestick chart with a 10-day moving average and volume bars (synthetic data). |
| 02 | [`02_compound_interest.py`](finance/02_compound_interest.py) | Growth of 1,000 at several annual rates. |
| 03 | [`03_present_value.py`](finance/03_present_value.py) | Present value of a cash-flow stream: each flow is discounted back to today. |
| 04 | [`04_yield_curve.py`](finance/04_yield_curve.py) | Normal, flat and inverted yield curves from a three-factor (Nelson-Siegel) shape. |
| 05 | [`05_option_payoffs.py`](finance/05_option_payoffs.py) | Profit at expiry of a long call, long put, long straddle and bull call spread. |
| 06 | [`06_efficient_frontier.py`](finance/06_efficient_frontier.py) | Mean-variance frontier of three assets, the tangency portfolio and the capital market line. |
| 07 | [`07_amortization.py`](finance/07_amortization.py) | Yearly interest and principal paid on a 30-year fixed-rate mortgage. |
| 08 | [`08_supply_demand.py`](finance/08_supply_demand.py) | Supply and demand with the equilibrium and the consumer and producer surplus. |
| 09 | [`09_black_scholes.py`](finance/09_black_scholes.py) | Black-Scholes European call price against spot, with the delta that is its slope. |
| 10 | [`10_bond_convexity.py`](finance/10_bond_convexity.py) | Bond price against yield: convexity, and the duration tangent that approximates it. |

### Logic (`examples/logic/`)

| # | Script | Figure |
|---|--------|--------|
| 01 | [`01_truth_tables.py`](logic/01_truth_tables.py) | Truth tables of four two-input Boolean functions. |
| 02 | [`02_logic_gates.py`](logic/02_logic_gates.py) | The six basic logic gate symbols, and a half adder built from two of them. |
| 03 | [`03_full_adder.py`](logic/03_full_adder.py) | A full adder built from gates, with every signal traced for one input case. |
| 04 | [`04_venn_de_morgan.py`](logic/04_venn_de_morgan.py) | Venn diagrams of two and three sets, with De Morgan's laws shaded. |
| 05 | [`05_karnaugh_map.py`](logic/05_karnaugh_map.py) | A four-variable Karnaugh map with its grouped prime implicants. |
| 06 | [`06_latch_flipflop.py`](logic/06_latch_flipflop.py) | An SR latch built from NOR gates, and a D flip-flop, each with a timing diagram. |
| 07 | [`07_binary_decision_diagram.py`](logic/07_binary_decision_diagram.py) | A reduced ordered binary decision diagram built from a truth table. |
| 08 | [`08_proof_tree.py`](logic/08_proof_tree.py) | A natural-deduction proof tree for hypothetical syllogism. |
| 09 | [`09_syllogism_euler.py`](logic/09_syllogism_euler.py) | Three valid syllogisms shown as Euler diagrams. |
| 10 | [`10_finite_automaton.py`](logic/10_finite_automaton.py) | A deterministic finite automaton for binary numbers divisible by three. |

## Executing the Gallery

To regenerate all diagrams and documentation artifacts across all domains:

```bash
uv run diagrams-as-code render examples --out output --format svg,png,bom
```

To run automated verification tests across the entire gallery:

```bash
uv run pytest tests/test_domain_examples.py tests/test_primitive_examples.py tests/test_technical_examples.py tests/test_textbook_examples.py tests/test_clinical_engineering_examples.py tests/test_golden_images.py
uv run diagrams-as-code lint examples
```
