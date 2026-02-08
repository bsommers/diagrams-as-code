from diagrams import Cluster, Diagram, Edge
from diagrams.onprem.iot import Sensor
import hivemq_theme as theme  # Import your separate module

with Diagram("Multi-Region Global Architecture",
             show=False,
             direction="LR",
             outformat="svg",
             graph_attr=theme.GLOBAL_ATTR):

    with Cluster("US-East (Primary)", graph_attr={"bgcolor": theme.DARK_GREY, "fontcolor": "white"}):
        us_edge = theme.get_icon("edge", "Baltimore Edge")
        us_broker = theme.get_icon("broker", "US Broker Cluster")

        Sensor("Factory Assets", **theme.BASE_NODE_ATTR) >> us_edge
        us_edge >> Edge(color=theme.HIVEMQ_YELLOW, label="spB / TLS") >> us_broker

    with Cluster("EU-West (Disaster Recovery)", graph_attr={"bgcolor": theme.DARK_GREY, "fontcolor": "white"}):
        eu_broker = theme.get_icon("cloud", "EU DR Cluster")

    # Multi-Region Bridge
    us_broker >> Edge(
        label="Cloud-to-Cloud Bridge",
        color=theme.HIVEMQ_YELLOW,
        style="dashed",
        fontcolor=theme.HIVEMQ_YELLOW
    ) >> eu_broker
