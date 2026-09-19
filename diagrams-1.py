from diagrams import Cluster, Diagram, Edge
from diagrams.custom import Custom
from diagrams.onprem.iot import Sensor
from diagrams.onprem.network import Internet

# Custom attributes for the HiveMQ Black and Gold theme
graph_attr = {
    "bgcolor": "#000000",
    "fontcolor": "#F3B01C",
    "fontsize": "20",
}

node_attr = {
    "fontcolor": "#000000",
    "fillcolor": "#F3B01C",
    "style": "filled",
    "shape": "box",
}

with Diagram("Industrial IoT: HiveMQ Edge to Cloud", show=False, direction="LR", graph_attr=graph_attr):
    
    with Cluster("Industrial Floor (Edge)", graph_attr={"bgcolor": "#1A1A1A", "fontcolor": "#F3B01C"}):
        sensors = [Sensor("PLC / Modbus", **node_attr),
                   Sensor("OPC UA Server", **node_attr)]
        
        # HiveMQ Edge acting as the local gateway
        edge_gateway = Custom("HiveMQ Edge", "./hivemq_logo.png", **{"fontcolor": "#F3B01C"}) 
        # Note: If you don't have a local png, use a standard icon:
        # from diagrams.onprem.edge import Server
        # edge_gateway = Server("HiveMQ Edge", **node_attr)

        sensors >> Edge(color="#F3B01C", style="dashed") >> edge_gateway

    with Cluster("Enterprise / Cloud", graph_attr={"bgcolor": "#1A1A1A", "fontcolor": "#F3B01C"}):
        # Central HiveMQ Broker
        central_broker = Custom("HiveMQ Broker", "./hivemq_logo.png", **{"fontcolor": "#F3B01C"})
        
        # Consumers
        analytics = Custom("Data Lake", "", **node_attr)
        dashboard = Custom("ERP/MES", "", **node_attr)

    # Connection from Edge to Central Broker via MQTT
    edge_gateway >> Edge(label="MQTT over TLS", color="#F3B01C", fontcolor="#F3B01C") >> central_broker
    
    central_broker >> Edge(color="#F3B01C") >> [analytics, dashboard]