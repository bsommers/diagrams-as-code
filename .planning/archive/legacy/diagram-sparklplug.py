from diagrams import Cluster, Diagram, Edge
from diagrams.onprem.compute import Server
from diagrams.onprem.iot import Sensor
from diagrams.onprem.database import Influxdb
from diagrams.onprem.queue import Kafka
from diagrams.generic.device import Tablet

# IIoT Brand Colors
IIOT_GOLD = "#F3B01C"
IIOT_BLACK = "#000000"
DARK_GREY = "#242424"

graph_attr = {
    "bgcolor": IIOT_BLACK,
    "fontcolor": IIOT_GOLD,
    "fontsize": "28",
    "pad": "0.7"
}

node_attr = {
    "fontcolor": IIOT_GOLD,
    "fillcolor": DARK_GREY,
    "color": IIOT_GOLD,
    "style": "filled",
}

with Diagram("IIoT Unified Namespace (UNS) with Sparkplug B", show=False, direction="LR", graph_attr=graph_attr):
    
    with Cluster("Manufacturing Cell", graph_attr={"bgcolor": "#111111", "fontcolor": IIOT_GOLD}):
        plc_assets = Sensor("Sensors & PLCs\n(Raw Data)", **node_attr)
        
        # IIoT Edge - The "EoN" (Edge of Network) Node
        eon_node = Server("IIoT Edge\n(Sparkplug B Host)", **node_attr)
        
        plc_assets >> Edge(color=IIOT_GOLD, label="Modbus/OPC UA") >> eon_node

    with Cluster("Enterprise UNS (Central IIoT)", graph_attr={"bgcolor": "#111111", "fontcolor": IIOT_GOLD}):
        uns_broker = Server("IIoT Broker\n(State Provider)", **node_attr)
        
        with Cluster("State Consumers"):
            kafka = Kafka("Kafka\n(Data Lake)", **node_attr)
            influx = Influxdb("InfluxDB\n(Historian)", **node_attr)
            scada = Tablet("Ignition / SCADA\n(Primary App)", **node_attr)

    # The Sparkplug B Communication
    # Topic: spBv1.0/Plant1/DDATA/Line1/Cell1
    eon_node >> Edge(label="spBv1.0 Payload", color=IIOT_GOLD, fontcolor=IIOT_GOLD) >> uns_broker
    
    # Decoupled consumption via Extensions
    uns_broker >> Edge(label="Extension", color=IIOT_GOLD) >> kafka
    uns_broker >> Edge(label="Extension", color=IIOT_GOLD) >> influx
    uns_broker >> Edge(label="MQTT Subscription", color=IIOT_GOLD) >> scada