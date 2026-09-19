from diagrams import Cluster, Diagram, Edge
from diagrams.custom import Custom
from diagrams.onprem.iot import Sensor
from diagrams.aws.compute import EC2
from diagrams.onprem.monitoring import Grafana

# HiveMQ Branding
HIVEMQ_YELLOW = "#FFC000"
HIVEMQ_BLACK = "#000000"
DARK_GREY = "#1A1A1A"

graph_attr = {
    "bgcolor": HIVEMQ_BLACK,
    "fontcolor": HIVEMQ_YELLOW,
    "fontsize": "30",
}

node_attr = {
    "fontcolor": HIVEMQ_BLACK,
    "fillcolor": HIVEMQ_YELLOW,
    "style": "filled",
}

with Diagram("HiveMQ: Edge-to-Cloud Bridge", show=False, direction="LR", graph_attr=graph_attr):
    
    with Cluster("On-Premise (Baltimore Plant)", graph_attr={"bgcolor": DARK_GREY, "fontcolor": "white"}):
        factory_data = Sensor("OPC UA / Modbus", **node_attr)
        # Local Edge Instance
        edge_node = Custom("HiveMQ Edge", "./hivemq_logo.png")
        
        factory_data >> Edge(color=HIVEMQ_YELLOW) >> edge_node

    with Cluster("HiveMQ Cloud (Managed)", graph_attr={"bgcolor": DARK_GREY, "fontcolor": "white"}):
        # The Cloud Broker
        cloud_broker = Custom("HiveMQ Cloud", "./hivemq_logo.png")
        
    with Cluster("Remote Monitoring", graph_attr={"bgcolor": DARK_GREY, "fontcolor": "white"}):
        hq_dashboard = Grafana("Executive View", **node_attr)

    # Secure Bridge connection
    edge_node >> Edge(label="Secure MQTT Bridge", color=HIVEMQ_YELLOW, fontcolor=HIVEMQ_YELLOW) >> cloud_broker
    cloud_broker >> Edge(color=HIVEMQ_YELLOW) >> hq_dashboard