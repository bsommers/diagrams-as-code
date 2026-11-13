# Diagrams-as-Code: Domain Examples Gallery

This directory contains 88 production-grade architecture and workflow diagrams spanning 8 primary domains, built entirely using the pure standard-library `diagrams_as_code` engine. Each example generates an SVG vector graphic, PNG rasterized image, and Bill of Materials (BOM) markdown document in `output/<domain>/`.

---

## Suite Summary & Metrics

- **Total Diagrams:** 88
- **Domains Covered:** 8 (`cloud`, `ai`, `computer`, `datacenter`, `business_process`, `cybersecurity`, `network_engineering`, `iiot`)
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

## 9. Technical Drawing Primitives (`examples/primitives/`)

Nine focused figures, one per primitive family, all in the `paper` theme. They are separate from the 88 domain diagrams above.

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

## Executing the Gallery

To regenerate all diagrams and documentation artifacts across all domains:

```bash
uv run diagrams-as-code render examples --out output --format svg,png,bom
```

To run automated verification tests across the entire gallery:

```bash
uv run pytest tests/test_domain_examples.py tests/test_primitive_examples.py
```

