# Mobile Offline-First Database Sync

![Architecture Diagram](./06_mobile_client_sync.svg)

## Bill of Materials

| Symbol / ID | Label | Kind | Group | Technical Notes / Metadata |
| :--- | :--- | :--- | :--- | :--- |
| `mobile_app` | **Field Technician App** | box | Mobile Client | os: iOS / Android React Native |
| `sqlite` | **Encrypted SQLite DB (SQLCipher)** | box | Mobile Client | encryption: 256-bit AES |
| `sync_mgr` | **Background Sync Engine** | box | Mobile Client | strategy: CRDT / Delta Sync |
| `ws_gateway` | **WebSocket Sync Gateway** | box | Cloud Endpoint | protocol: WSS Secure Sockets |
| `cloud_db` | **Master PostgreSQL DB** | box | Cloud Endpoint | ha: Multi-Region Read-Write |

## Connections

| Source | Target | Protocol / Label | Style | Routing |
| :--- | :--- | :--- | :--- | :--- |
| **Field Technician App** (`mobile_app`) | **Encrypted SQLite DB (SQLCipher)** (`sqlite`) | Local CRUD Queries | solid | orthogonal |
| **Encrypted SQLite DB (SQLCipher)** (`sqlite`) | **Background Sync Engine** (`sync_mgr`) | Queued Mutations | dashed | orthogonal |
| **Background Sync Engine** (`sync_mgr`) | **WebSocket Sync Gateway** (`ws_gateway`) | TLS WebSocket Sync | solid | orthogonal |
| **WebSocket Sync Gateway** (`ws_gateway`) | **Master PostgreSQL DB** (`cloud_db`) | Commit Resolved Transactions | solid | orthogonal |
