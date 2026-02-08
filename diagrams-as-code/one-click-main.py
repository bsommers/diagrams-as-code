from diagrams import Diagram

from hivemq_theme import HIVEMQ_YELLOW, HiveMQPalette

palette = HiveMQPalette("icons.yaml")
diag_name = "Baltimore_UNS_Standard"
img_file = f"{diag_name}.svg"

with Diagram(diag_name, show=False, outformat="svg", filename=diag_name):
    # Your logic here
    edge = palette.get_node("edge", "Maryland Plant")
    # ...

palette.generate_readme(diag_name, img_file)

# Choice 1: Push to your HiveMQ GitHub repo
# palette.push_to_github('.')

# Choice 2: Upload to your S3 Documentation bucket
# palette.upload_to_s3([img_file, 'README.md'], 'my-hivemq-docs-bucket')
