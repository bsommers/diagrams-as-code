import csv
import os
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
        self.csv_path = csv_path
        self.icon_map = {}
        self._bootstrap()
        self.load_icons()

    def _bootstrap(self):
        """Ensures the directory structure and CSV template exist."""
        # Create icons folder if missing
        if not os.path.exists('icons'):
            os.makedirs('icons')
            print("Created directory: /icons")

        # Create template CSV if missing
        if not os.path.exists(self.csv_path):
            with open(self.csv_path, mode='w', newline='') as f:
                writer = csv.writer(f)
                writer.writerow(['symbol', 'path', 'notes'])
                writer.writerow(['edge', './icons/hivemq_edge.png', 'Industrial Edge Gateway'])
                writer.writerow(['broker', './icons/hivemq_broker.png', 'Enterprise Broker Cluster'])
            print(f"Generated template file: {self.csv_path}")

    def load_icons(self):
        with open(self.csv_path, mode='r') as f:
            reader = csv.DictReader(f)
            for row in reader:
                self.icon_map[row['symbol'].lower()] = row['path']

    def get_node(self, symbol, label):
        path = self.icon_map.get(symbol.lower(), "./icons/default.png")
        # Log the note if you want to see metadata in the console
        return Custom(label, path)
