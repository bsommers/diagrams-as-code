from diagrams import Cluster, Diagram, Edge
from diagrams.custom import Custom
from diagrams.onprem.iot import Sensor
from diagrams.onprem.queue import Kafka
from diagrams.onprem.database import Influxdb

# Official HiveMQ Brand Palette
HIVEMQ_YELLOW = "#FFC000"
HIVEMQ_BLACK = "#000000"
OFF_WHITE = "#FFFFFF"

graph_attr = {
    "bgcolor": HIVEMQ_BLACK,
    "fontcolor": HIVEMQ_YELLOW,
    "fontsize": "30",
    "pad": "1.0"
}

# Standard style for non-HiveMQ nodes
node_attr = {
    "fontcolor": HIVEMQ_BLACK,
    "fillcolor": HIVEMQ_YELLOW,
    "style": "filled",
}

with Diagram("HiveMQ Industrial Data Fabric", show=False, direction="LR", graph_attr=graph_attr):
    
    with Cluster("The Edge (OT)", graph_attr={"bgcolor": "#1A1A1A", "fontcolor": OFF_WHITE}):
        plcs = Sensor("Factory Assets", **node_attr)
        
        # Using the official logo for HiveMQ Edge
        edge = Custom("HiveMQ Edge", "./hivemq_logo.png")
        
        plcs >> Edge(color=HIVEMQ_YELLOW, label="Modbus/OPC UA") >> edge

    with Cluster("Enterprise Core (IT)", graph_attr={"bgcolor": "#1A1A1A", "fontcolor": OFF_WHITE}):
        # Using the official logo for the Broker
        broker = Custom("HiveMQ Platform", "./hivemq_logo.png")
        
        with Cluster("Analytics Stack"):
            kafka = Kafka("Kafka Stream", **node_attr)
            influx = Influxdb("Historian", **node_attr)

    # Bridge with high-contrast labeling
    edge >> Edge(label="Sparkplug B / TLS", color=HIVEMQ_YELLOW, fontcolor=HIVEMQ_YELLOW) >> broker
    broker >> Edge(color=HIVEMQ_YELLOW) >> [kafka, influx]