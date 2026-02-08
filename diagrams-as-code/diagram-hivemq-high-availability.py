from diagrams import Cluster, Diagram, Edge
from diagrams.custom import Custom
from diagrams.onprem.iot import Sensor
from diagrams.onprem.network import Internet
from diagrams.aws.network import ELB # Using AWS ELB as a Load Balancer example

# HiveMQ Branding
HIVEMQ_YELLOW = "#FFC000"
HIVEMQ_BLACK = "#000000"
DARK_GREY = "#1A1A1A"

graph_attr = {
    "bgcolor": HIVEMQ_BLACK,
    "fontcolor": HIVEMQ_YELLOW,
    "fontsize": "32",
    "pad": "1.0"
}

node_attr = {
    "fontcolor": HIVEMQ_BLACK,
    "fillcolor": HIVEMQ_YELLOW,
    "style": "filled",
}

with Diagram("HiveMQ_High_Availability_UNS", 
             show=False, 
             direction="LR", 
             outformat="svg", 
             graph_attr=graph_attr):

    with Cluster("Production Site (Baltimore)", graph_attr={"bgcolor": DARK_GREY, "fontcolor": "white"}):
        edge_node = Custom("HiveMQ Edge", "./hivemq_logo.png")
        sensors = Sensor("Plant Assets", **node_attr)
        sensors >> Edge(color="white") >> edge_node

    # Entry Point
    lb = ELB("Load Balancer", **node_attr)

    with Cluster("HiveMQ HA Cluster (Control Plane)", graph_attr={"bgcolor": "#333333", "fontcolor": HIVEMQ_YELLOW}):
        # Multiple nodes to show redundancy
        nodes = [Custom("Node 1", "./hivemq_logo.png"),
                 Custom("Node 2", "./hivemq_logo.png"),
                 Custom("Node 3", "./hivemq_logo.png")]

    # Data Flow
    edge_node >> Edge(label="MQTT / TLS", color=HIVEMQ_YELLOW, fontcolor=HIVEMQ_YELLOW) >> lb
    lb >> Edge(color=HIVEMQ_YELLOW) >> nodes

    # Representation of State Sharing
    nodes[0] - Edge(color=HIVEMQ_YELLOW, style="dotted", label="Cluster Discovery") - nodes[1]
    nodes[1] - Edge(color=HIVEMQ_YELLOW, style="dotted") - nodes[2]