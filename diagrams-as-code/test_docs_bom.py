from diagrams import Diagram, Edge
from hivemq_theme import HiveMQPalette, GLOBAL_ATTR

palette = HiveMQPalette('icons.yaml')
diag_name = "Baltimore_Plant_UNS"
img_file = f"{diag_name}.svg"

with Diagram(diag_name, show=False, outformat="svg", filename=diag_name, graph_attr=GLOBAL_ATTR):
    edge = palette.get_node("edge", "Maryland Edge")
    broker = palette.get_node("broker", "HiveMQ Cloud")
    edge >> Edge(label="MQTT/TLS", color="#FFC000") >> broker

# Call this to wrap everything up
palette.generate_readme(diag_name, img_file)

