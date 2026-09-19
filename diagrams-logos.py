from diagrams import Cluster, Diagram, Edge
from diagrams.custom import Custom
from diagrams.onprem.iot import Sensor
from diagrams.onprem.queue import Kafka
from diagrams.onprem.database import Influxdb

# Official IIoT Brand Palette
IIOT_YELLOW = "#FFC000"
IIOT_BLACK = "#000000"
OFF_WHITE = "#FFFFFF"

graph_attr = {
    "bgcolor": IIOT_BLACK,
    "fontcolor": IIOT_YELLOW,
    "fontsize": "30",
    "pad": "1.0"
}

# Standard style for non-IIoT nodes
node_attr = {
    "fontcolor": IIOT_BLACK,
    "fillcolor": IIOT_YELLOW,
    "style": "filled",
}

with Diagram("IIoT Industrial Data Fabric", show=False, direction="LR", graph_attr=graph_attr):
    
    with Cluster("The Edge (OT)", graph_attr={"bgcolor": "#1A1A1A", "fontcolor": OFF_WHITE}):
        plcs = Sensor("Factory Assets", **node_attr)
        
        # Using the official logo for IIoT Edge
        edge = Custom("IIoT Edge", "./iiot_logo.png")
        
        plcs >> Edge(color=IIOT_YELLOW, label="Modbus/OPC UA") >> edge

    with Cluster("Enterprise Core (IT)", graph_attr={"bgcolor": "#1A1A1A", "fontcolor": OFF_WHITE}):
        # Using the official logo for the Broker
        broker = Custom("IIoT Platform", "./iiot_logo.png")
        
        with Cluster("Analytics Stack"):
            kafka = Kafka("Kafka Stream", **node_attr)
            influx = Influxdb("Historian", **node_attr)

    # Bridge with high-contrast labeling
    edge >> Edge(label="Sparkplug B / TLS", color=IIOT_YELLOW, fontcolor=IIOT_YELLOW) >> broker
    broker >> Edge(color=IIOT_YELLOW) >> [kafka, influx]