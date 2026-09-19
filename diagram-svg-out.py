from diagrams import Cluster, Diagram, Edge
from diagrams.custom import Custom
from diagrams.onprem.iot import Sensor
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

# Added outformat="svg" below
with Diagram("HiveMQ_Architecture_Vector", 
             show=False, 
             direction="LR", 
             outformat="svg", 
             graph_attr=graph_attr):
    
    with Cluster("On-Premise (Baltimore Plant)", graph_attr={"bgcolor": DARK_GREY, "fontcolor": "white"}):
        factory_data = Sensor("OPC UA / Modbus", **node_attr)
        edge_node = Custom("HiveMQ Edge", "./hivemq_logo.png")
        factory_data >> Edge(color=HIVEMQ_YELLOW) >> edge_node

    with Cluster("HiveMQ Cloud", graph_attr={"bgcolor": DARK_GREY, "fontcolor": "white"}):
        cloud_broker = Custom("Managed Broker", "./hivemq_logo.png")
        
    hq_dashboard = Grafana("Executive View", **node_attr)

    edge_node >> Edge(label="Secure MQTT Bridge", color=HIVEMQ_YELLOW, fontcolor=HIVEMQ_YELLOW) >> cloud_broker
    cloud_broker >> Edge(color=HIVEMQ_YELLOW) >> hq_dashboard