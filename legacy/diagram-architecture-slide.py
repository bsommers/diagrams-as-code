from diagrams import Cluster, Diagram, Edge
from diagrams.custom import Custom
from diagrams.onprem.iot import Sensor
from diagrams.onprem.monitoring import Grafana
from diagrams.generic.blank import Blank

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

with Diagram("IIoT_Client_Reference_UNS",
             show=False,
             direction="LR",
             outformat="svg",
             graph_attr=graph_attr):

    # Legend Section
    with Cluster("Diagram Legend", graph_attr={"bgcolor": "#333333", "fontcolor": "white"}):
        Legend_MQTT = Blank("Gold Line = MQTT TLS", **{"fontcolor": IIOT_YELLOW, "width": "2"})
        Legend_Data = Blank("Thin Line = Raw Data", **{"fontcolor": "white", "width": "2"})

    # On-Premise Section
    with Cluster("Production Site (Baltimore)", graph_attr={"bgcolor": DARK_GREY, "fontcolor": "white"}):
        plc = Sensor("Allen-Bradley PLC", **node_attr)
        edge = Custom("IIoT Edge", "./iiot_logo.png")

        # Raw data flow
        plc >> Edge(color="white", label="Modbus/TCP") >> edge

    # Cloud Section
    with Cluster("Enterprise UNS (IIoT Cloud)", graph_attr={"bgcolor": DARK_GREY, "fontcolor": "white"}):
        cloud_broker = Custom("Central Broker", "./iiot_logo.png")

    # Consumer
    hq_dashboard = Grafana("Grafana Cloud", **node_attr)

    # Labeled Topic Flow
    edge >> Edge(
        label="spBv1.0/Baltimore/DDATA/Line1/Cell1",
        color=IIOT_YELLOW,
        fontcolor=IIOT_YELLOW
    ) >> cloud_broker

    cloud_broker >> Edge(
        label="Subscribe: #",
        color=IIOT_YELLOW,
        fontcolor=IIOT_YELLOW
    ) >> hq_dashboard
