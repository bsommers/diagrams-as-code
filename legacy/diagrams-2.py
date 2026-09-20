from diagrams import Cluster, Diagram, Edge
from diagrams.onprem.compute import Server
from diagrams.onprem.iot import Sensor
from diagrams.onprem.database import SQL
from diagrams.programming.language import Python

# IIoT Brand Colors
IIOT_GOLD = "#F3B01C"
IIOT_BLACK = "#000000"
DARK_GREY = "#242424"

graph_attr = {
    "bgcolor": IIOT_BLACK,
    "fontcolor": IIOT_GOLD,
    "fontsize": "25",
    "pad": "0.5"
}

node_attr = {
    "fontcolor": IIOT_GOLD,
    "fillcolor": DARK_GREY,
    "color": IIOT_GOLD,
    "style": "filled",
}

with Diagram("Industrial MQTT Architecture", show=False, direction="LR", graph_attr=graph_attr):
    
    with Cluster("Production Site (Plant Floor)", graph_attr={"bgcolor": "#111111", "fontcolor": IIOT_GOLD}):
        with Cluster("Legacy Assets"):
            assets = [Sensor("PLCs (Modbus)", **node_attr),
                      Sensor("OPC UA Nodes", **node_attr)]
        
        # IIoT Edge
        edge = Server("IIoT Edge \n Gateway", **node_attr)
        
        assets >> Edge(color=IIOT_GOLD, label="Protocol Translation") >> edge

    with Cluster("Enterprise Cloud / Data Center", graph_attr={"bgcolor": "#111111", "fontcolor": IIOT_GOLD}):
        # Central Broker
        broker = Server("IIoT Broker \n (Cluster)", **node_attr)
        
        # Consumers
        storage = SQL("TimescaleDB / Influx", **node_attr)
        ml_app = Python("ML Analytics", **node_attr)

    # The Bridge
    edge >> Edge(label="MQTT Bridge (TLS)", color=IIOT_GOLD, fontcolor=IIOT_GOLD) >> broker
    broker >> Edge(color=IIOT_GOLD) >> [storage, ml_app]