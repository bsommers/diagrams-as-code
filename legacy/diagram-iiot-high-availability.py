from diagrams import Cluster, Diagram, Edge
from diagrams.custom import Custom
from diagrams.onprem.iot import Sensor
from diagrams.onprem.network import Internet
from diagrams.aws.network import ELB # Using AWS ELB as a Load Balancer example

# IIoT Branding
IIOT_YELLOW = "#FFC000"
IIOT_BLACK = "#000000"
DARK_GREY = "#1A1A1A"

graph_attr = {
    "bgcolor": IIOT_BLACK,
    "fontcolor": IIOT_YELLOW,
    "fontsize": "32",
    "pad": "1.0"
}

node_attr = {
    "fontcolor": IIOT_BLACK,
    "fillcolor": IIOT_YELLOW,
    "style": "filled",
}

with Diagram("IIoT_High_Availability_UNS", 
             show=False, 
             direction="LR", 
             outformat="svg", 
             graph_attr=graph_attr):

    with Cluster("Production Site (Baltimore)", graph_attr={"bgcolor": DARK_GREY, "fontcolor": "white"}):
        edge_node = Custom("IIoT Edge", "./iiot_logo.png")
        sensors = Sensor("Plant Assets", **node_attr)
        sensors >> Edge(color="white") >> edge_node

    # Entry Point
    lb = ELB("Load Balancer", **node_attr)

    with Cluster("IIoT HA Cluster (Control Plane)", graph_attr={"bgcolor": "#333333", "fontcolor": IIOT_YELLOW}):
        # Multiple nodes to show redundancy
        nodes = [Custom("Node 1", "./iiot_logo.png"),
                 Custom("Node 2", "./iiot_logo.png"),
                 Custom("Node 3", "./iiot_logo.png")]

    # Data Flow
    edge_node >> Edge(label="MQTT / TLS", color=IIOT_YELLOW, fontcolor=IIOT_YELLOW) >> lb
    lb >> Edge(color=IIOT_YELLOW) >> nodes

    # Representation of State Sharing
    nodes[0] - Edge(color=IIOT_YELLOW, style="dotted", label="Cluster Discovery") - nodes[1]
    nodes[1] - Edge(color=IIOT_YELLOW, style="dotted") - nodes[2]