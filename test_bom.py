from diagrams import Diagram
from hivemq_theme import HiveMQPalette, GLOBAL_ATTR

palette = HiveMQPalette('icons.yaml')

with Diagram("Baltimore Industrial UNS", show=False, outformat="svg", graph_attr=GLOBAL_ATTR):
    edge = palette.get_node("edge", "Maryland Plant Edge")
    # ... rest of your logic ...

# Generate the manifest in the console
palette.print_bom()

