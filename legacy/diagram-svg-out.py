from diagrams import Cluster, Diagram, Edge
from diagrams.custom import Custom
from diagrams.onprem.iot import Sensor
from diagrams.onprem.monitoring import Grafana

# IIoT Branding
IIOT_YELLOW = "#FFC000"
IIOT_BLACK = "#000000"
DARK_GREY = "#1A1A1A"

graph_attr = {
    "bgcolor": IIOT_BLACK,
    "fontcolor": IIOT_YELLOW,
    "fontsize": "30",
}

node_attr = {
    "fontcolor": IIOT_BLACK,
    "fillcolor": IIOT_YELLOW,
    "style": "filled",
}

# Added outformat="svg" below
with Diagram("IIoT_Architecture_Vector", 
             show=False, 
             direction="LR", 
             outformat="svg", 
             graph_attr=graph_attr):
    
    with Cluster("On-Premise (Baltimore Plant)", graph_attr={"bgcolor": DARK_GREY, "fontcolor": "white"}):
        factory_data = Sensor("OPC UA / Modbus", **node_attr)
        edge_node = Custom("IIoT Edge", "./iiot_logo.png")
        factory_data >> Edge(color=IIOT_YELLOW) >> edge_node

    with Cluster("IIoT Cloud", graph_attr={"bgcolor": DARK_GREY, "fontcolor": "white"}):
        cloud_broker = Custom("Managed Broker", "./iiot_logo.png")
        
    hq_dashboard = Grafana("Executive View", **node_attr)

    edge_node >> Edge(label="Secure MQTT Bridge", color=IIOT_YELLOW, fontcolor=IIOT_YELLOW) >> cloud_broker
    cloud_broker >> Edge(color=IIOT_YELLOW) >> hq_dashboard