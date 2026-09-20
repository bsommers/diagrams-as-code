from diagrams import Cluster, Diagram, Edge
from diagrams.onprem.compute import Server
from diagrams.onprem.iot import Sensor
from diagrams.onprem.database import Influxdb
from diagrams.onprem.queue import Kafka
from diagrams.onprem.monitoring import Grafana

# IIoT Brand Colors
IIOT_GOLD = "#F3B01C"
IIOT_BLACK = "#000000"
DARK_GREY = "#242424"

graph_attr = {
    "bgcolor": IIOT_BLACK,
    "fontcolor": IIOT_GOLD,
    "fontsize": "25",
    "pad": "0.5"
}

node_attr = {
    "fontcolor": IIOT_GOLD,
    "fillcolor": DARK_GREY,
    "color": IIOT_GOLD,
    "style": "filled",
}

with Diagram("Industrial Data Pipeline: Edge to Enterprise", show=False, direction="LR", graph_attr=graph_attr):
    
    with Cluster("Plant Floor", graph_attr={"bgcolor": "#111111", "fontcolor": IIOT_GOLD}):
        field_devices = [Sensor("Modbus TCP", **node_attr),
                         Sensor("OPC UA", **node_attr)]
        
        edge_gateway = Server("IIoT Edge", **node_attr)
        field_devices >> Edge(color=IIOT_GOLD) >> edge_gateway

    with Cluster("Enterprise Cloud / Cluster", graph_attr={"bgcolor": "#111111", "fontcolor": IIOT_GOLD}):
        broker_cluster = Server("IIoT Enterprise", **node_attr)
        
        with Cluster("Data Consumers"):
            kafka_stream = Kafka("Confluent/Kafka", **node_attr)
            time_series = Influxdb("InfluxDB", **node_attr)
            dashboard = Grafana("Real-time Stats", **node_attr)

    # MQTT Bridge with TLS
    edge_gateway >> Edge(label="MQTT Bridge (TLS)", color=IIOT_GOLD, fontcolor=IIOT_GOLD) >> broker_cluster
    
    # Extensions logic
    broker_cluster >> Edge(label="Kafka Extension", color=IIOT_GOLD, fontcolor=IIOT_GOLD) >> kafka_stream
    broker_cluster >> Edge(label="InfluxDB Extension", color=IIOT_GOLD, fontcolor=IIOT_GOLD) >> time_series
    time_series >> Edge(color=IIOT_GOLD) >> dashboard