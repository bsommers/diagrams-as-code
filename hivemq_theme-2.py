import csv
from diagrams.custom import Custom

# HiveMQ Branding
HIVEMQ_YELLOW = "#FFC000"
HIVEMQ_BLACK = "#000000"
DARK_GREY = "#1A1A1A"

GLOBAL_ATTR = {
    "bgcolor": HIVEMQ_BLACK,
    "fontcolor": HIVEMQ_YELLOW,
    "fontsize": "32",
}

BASE_NODE_ATTR = {
    "fontcolor": HIVEMQ_BLACK,
    "fillcolor": HIVEMQ_YELLOW,
    "style": "filled",
}

class HiveMQPalette:
    def __init__(self, csv_path='icons.csv'):
        self.icon_map = {}
        self.load_icons(csv_path)

    def load_icons(self, path):
        try:
            with open(path, mode='r') as f:
                reader = csv.DictReader(f)
                for row in reader:
                    # Maps the symbol key to the file path
                    self.icon_map[row['symbol'].lower()] = row['path']
        except FileNotFoundError:
            print(f"Warning: {path} not found. Using empty icon map.")

    def get_node(self, symbol, label):
        path = self.icon_map.get(symbol.lower(), "./icons/default.png")
        return Custom(label, path)