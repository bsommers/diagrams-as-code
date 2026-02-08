from diagrams import Cluster, Diagram, Edge
from diagrams.onprem.compute import Server
from diagrams.onprem.iot import Sensor
from diagrams.onprem.database import Influxdb
from diagrams.onprem.queue import Kafka
from diagrams.onprem.monitoring import Grafana

# HiveMQ Brand Colors
HIVEMQ_GOLD = "#F3B01C"
HIVEMQ_BLACK = "#000000"
DARK_GREY = "#242424"

graph_attr = {
    "bgcolor": HIVEMQ_BLACK,
    "fontcolor": HIVEMQ_GOLD,
    "fontsize": "25",
    "pad": "0.5"
}

node_attr = {
    "fontcolor": HIVEMQ_GOLD,
    "fillcolor": DARK_GREY,
    "color": HIVEMQ_GOLD,
    "style": "filled",
}

with Diagram("Industrial Data Pipeline: Edge to Enterprise", show=False, direction="LR", graph_attr=graph_attr):
    
    with Cluster("Plant Floor", graph_attr={"bgcolor": "#111111", "fontcolor": HIVEMQ_GOLD}):
        field_devices = [Sensor("Modbus TCP", **node_attr),
                         Sensor("OPC UA", **node_attr)]
        
        edge_gateway = Server("HiveMQ Edge", **node_attr)
        field_devices >> Edge(color=HIVEMQ_GOLD) >> edge_gateway

    with Cluster("Enterprise Cloud / Cluster", graph_attr={"bgcolor": "#111111", "fontcolor": HIVEMQ_GOLD}):
        broker_cluster = Server("HiveMQ Enterprise", **node_attr)
        
        with Cluster("Data Consumers"):
            kafka_stream = Kafka("Confluent/Kafka", **node_attr)
            time_series = Influxdb("InfluxDB", **node_attr)
            dashboard = Grafana("Real-time Stats", **node_attr)

    # MQTT Bridge with TLS
    edge_gateway >> Edge(label="MQTT Bridge (TLS)", color=HIVEMQ_GOLD, fontcolor=HIVEMQ_GOLD) >> broker_cluster
    
    # Extensions logic
    broker_cluster >> Edge(label="Kafka Extension", color=HIVEMQ_GOLD, fontcolor=HIVEMQ_GOLD) >> kafka_stream
    broker_cluster >> Edge(label="InfluxDB Extension", color=HIVEMQ_GOLD, fontcolor=HIVEMQ_GOLD) >> time_series
    time_series >> Edge(color=HIVEMQ_GOLD) >> dashboard