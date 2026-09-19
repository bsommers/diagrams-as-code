from diagrams.custom import Custom

# HiveMQ Brand Constants
HIVEMQ_YELLOW = "#FFC000"
HIVEMQ_BLACK = "#000000"
DARK_GREY = "#1A1A1A"

# Global Diagram Attributes
GLOBAL_ATTR = {
    "bgcolor": HIVEMQ_BLACK,
    "fontcolor": HIVEMQ_YELLOW,
    "fontsize": "32",
    "pad": "1.0"
}

# Shared Node Attributes
BASE_NODE_ATTR = {
    "fontcolor": HIVEMQ_BLACK,
    "fillcolor": HIVEMQ_YELLOW,
    "style": "filled",
}

# Icon Mapping Table
# Maps a simple key to the local file path
ICON_MAP = {
    "edge": "./icons/hivemq_edge.png",
    "broker": "./icons/hivemq_broker.png",
    "cloud": "./icons/hivemq_cloud.png",
    "kafka": "./icons/kafka_gold.png",
}

def get_icon(key, label):
    """Returns a Custom node using the mapping table."""
    path = ICON_MAP.get(key.lower(), "./icons/default.png")
    return Custom(label, path)