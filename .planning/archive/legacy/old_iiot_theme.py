from diagrams.custom import Custom

# IIoT Brand Constants
IIOT_YELLOW = "#FFC000"
IIOT_BLACK = "#000000"
DARK_GREY = "#1A1A1A"

# Global Diagram Attributes
GLOBAL_ATTR = {
    "bgcolor": IIOT_BLACK,
    "fontcolor": IIOT_YELLOW,
    "fontsize": "32",
    "pad": "1.0"
}

# Shared Node Attributes
BASE_NODE_ATTR = {
    "fontcolor": IIOT_BLACK,
    "fillcolor": IIOT_YELLOW,
    "style": "filled",
}

# Icon Mapping Table
# Maps a simple key to the local file path
ICON_MAP = {
    "edge": "./icons/iiot_edge.png",
    "broker": "./icons/iiot_broker.png",
    "cloud": "./icons/iiot_cloud.png",
    "kafka": "./icons/kafka_gold.png",
}

def get_icon(key, label):
    """Returns a Custom node using the mapping table."""
    path = ICON_MAP.get(key.lower(), "./icons/default.png")
    return Custom(label, path)