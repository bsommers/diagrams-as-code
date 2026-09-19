import csv
import json
import os

import boto3
import yaml
from diagrams.custom import Custom
from git import Repo

# HiveMQ Branding
HIVEMQ_YELLOW = "#FFC000"
HIVEMQ_BLACK = "#000000"


class HiveMQPalette:
    def __init__(self, config_path="icons.yaml"):
        self.config_path = config_path
        self.icon_data = {}
        self.used_symbols = []
        self._bootstrap()
        self.load_icons()

    def _bootstrap(self):
        if not os.path.exists("icons"):
            os.makedirs("icons")
        if not os.path.exists(self.config_path):
            ext = os.path.splitext(self.config_path)[1].lower()
            default = [
                {
                    "symbol": "edge",
                    "path": "./icons/edge.png",
                    "notes": "HiveMQ Edge Gateway",
                }
            ]
            with open(self.config_path, "w") as f:
                if ext == ".json":
                    json.dump(default, f, indent=4)
                elif ext in [".yaml", ".yml"]:
                    yaml.dump(default, f)
                else:
                    writer = csv.DictWriter(f, fieldnames=["symbol", "path", "notes"])
                    writer.writeheader()
                    writer.writerows(default)

    def load_icons(self):
        ext = os.path.splitext(self.config_path)[1].lower()
        with open(self.config_path, "r") as f:
            if ext == ".json":
                data = json.load(f)
            elif ext in [".yaml", ".yml"]:
                data = yaml.safe_load(f)
            else:
                data = list(csv.DictReader(f))
            for entry in data:
                self.icon_data[entry["symbol"].lower()] = entry

    def get_node(self, symbol, label):
        sym_key = symbol.lower()
        node_info = self.icon_data.get(
            sym_key, {"path": "./icons/default.png", "notes": "Unknown"}
        )
        if sym_key not in [s["symbol"] for s in self.used_symbols]:
            self.used_symbols.append(
                {"symbol": sym_key, "label": label, "notes": node_info.get("notes", "")}
            )
        return Custom(label, node_info["path"])

    def generate_readme(self, diagram_name, image_file):
        with open("README.md", "w") as f:
            f.write(f"# {diagram_name.replace('_', ' ')}\n\n")
            f.write(f"![Architecture Diagram](./{image_file})\n\n")
            f.write("## Bill of Materials\n\n")
            f.write("| Symbol | Label | Technical Notes |\n| :--- | :--- | :--- |\n")
            for item in self.used_symbols:
                f.write(f"| {item['symbol']} | {item['label']} | {item['notes']} |\n")
        print("Generated README.md locally.")

    def push_to_github(self, repo_path, commit_msg="Automated diagram update"):
        """Commits and pushes changes to the current Git repository."""
        try:
            repo = Repo(repo_path)
            repo.git.add(all=True)
            repo.index.commit(commit_msg)
            origin = repo.remote(name="origin")
            origin.push()
            print("Successfully pushed to GitHub.")
        except Exception as e:
            print(f"Git Error: {e}")

    def upload_to_s3(self, file_list, bucket_name, region="us-east-1"):
        """Uploads the generated files to an S3 bucket for hosting."""
        s3 = boto3.client("s3", region_name=region)
        for file in file_list:
            try:
                s3.upload_file(file, bucket_name, file)
                print(f"Uploaded {file} to S3 bucket: {bucket_name}")
            except Exception as e:
                print(f"S3 Error: {e}")
