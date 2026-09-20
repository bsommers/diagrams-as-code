# Fibre Channel Storage Area Network (SAN)

![Architecture Diagram](./02_san_storage_fabric.svg)

## Bill of Materials

| Symbol / ID | Label | Kind | Group | Technical Notes / Metadata |
| :--- | :--- | :--- | :--- | :--- |
| `host_app` | **Enterprise Application Host** | box | Compute Hosts | hba: Dual 32G FC HBAs |
| `fc_switch_a` | **Brocade 32G FC Switch A** | box | Fabric A | zone: Storage Zone A |
| `fc_switch_b` | **Brocade 32G FC Switch B** | box | Fabric B | zone: Storage Zone B |
| `ctrl_a` | **Storage Controller A** | box | Storage Array | cache: 128GB Mirrored |
| `ctrl_b` | **Storage Controller B** | box | Storage Array | cache: 128GB Mirrored |
| `disk_shelf` | **24x NVMe SSD Drive Shelf** | box | Storage Array | capacity: 153 TB Raw |

## Connections

| Source | Target | Protocol / Label | Style | Routing |
| :--- | :--- | :--- | :--- | :--- |
| **Enterprise Application Host** (`host_app`) | **Brocade 32G FC Switch A** (`fc_switch_a`) | 32G FC Link | solid | orthogonal |
| **Enterprise Application Host** (`host_app`) | **Brocade 32G FC Switch B** (`fc_switch_b`) | 32G FC Link | dashed | orthogonal |
| **Brocade 32G FC Switch A** (`fc_switch_a`) | **Storage Controller A** (`ctrl_a`) | Target Port A1 | solid | orthogonal |
| **Brocade 32G FC Switch B** (`fc_switch_b`) | **Storage Controller B** (`ctrl_b`) | Target Port B1 | dashed | orthogonal |
| **Storage Controller A** (`ctrl_a`) | **24x NVMe SSD Drive Shelf** (`disk_shelf`) | SAS-4 24G Loop | solid | orthogonal |
| **Storage Controller B** (`ctrl_b`) | **24x NVMe SSD Drive Shelf** (`disk_shelf`) | SAS-4 24G Loop | dashed | orthogonal |
