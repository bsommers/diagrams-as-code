from diagrams import Cluster, Diagram, Edge
from diagrams.onprem.compute import Server
from diagrams.onprem.iot import Sensor
from diagrams.onprem.database import Influxdb
from diagrams.onprem.queue import Kafka
from diagrams.generic.device import Tablet

# HiveMQ Brand Colors
HIVEMQ_GOLD = "#F3B01C"
HIVEMQ_BLACK = "#000000"
DARK_GREY = "#242424"

graph_attr = {
    "bgcolor": HIVEMQ_BLACK,
    "fontcolor": HIVEMQ_GOLD,
    "fontsize": "28",
    "pad": "0.7"
}

node_attr = {
    "fontcolor": HIVEMQ_GOLD,
    "fillcolor": DARK_GREY,
    "color": HIVEMQ_GOLD,
    "style": "filled",
}

with Diagram("HiveMQ Unified Namespace (UNS) with Sparkplug B", show=False, direction="LR", graph_attr=graph_attr):
    
    with Cluster("Manufacturing Cell", graph_attr={"bgcolor": "#111111", "fontcolor": HIVEMQ_GOLD}):
        plc_assets = Sensor("Sensors & PLCs\n(Raw Data)", **node_attr)
        
        # HiveMQ Edge - The "EoN" (Edge of Network) Node
        eon_node = Server("HiveMQ Edge\n(Sparkplug B Host)", **node_attr)
        
        plc_assets >> Edge(color=HIVEMQ_GOLD, label="Modbus/OPC UA") >> eon_node

    with Cluster("Enterprise UNS (Central HiveMQ)", graph_attr={"bgcolor": "#111111", "fontcolor": HIVEMQ_GOLD}):
        uns_broker = Server("HiveMQ Broker\n(State Provider)", **node_attr)
        
        with Cluster("State Consumers"):
            kafka = Kafka("Kafka\n(Data Lake)", **node_attr)
            influx = Influxdb("InfluxDB\n(Historian)", **node_attr)
            scada = Tablet("Ignition / SCADA\n(Primary App)", **node_attr)

    # The Sparkplug B Communication
    # Topic: spBv1.0/Plant1/DDATA/Line1/Cell1
    eon_node >> Edge(label="spBv1.0 Payload", color=HIVEMQ_GOLD, fontcolor=HIVEMQ_GOLD) >> uns_broker
    
    # Decoupled consumption via Extensions
    uns_broker >> Edge(label="Extension", color=HIVEMQ_GOLD) >> kafka
    uns_broker >> Edge(label="Extension", color=HIVEMQ_GOLD) >> influx
    uns_broker >> Edge(label="MQTT Subscription", color=HIVEMQ_GOLD) >> scada