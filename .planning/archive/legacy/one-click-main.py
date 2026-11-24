from diagrams import Diagram

from iiot_theme import IIOT_YELLOW, IIoTPalette

palette = IIoTPalette("icons.yaml")
diag_name = "Baltimore_UNS_Standard"
img_file = f"{diag_name}.svg"

with Diagram(diag_name, show=False, outformat="svg", filename=diag_name):
    # Your logic here
    edge = palette.get_node("edge", "Maryland Plant")
    # ...

palette.generate_readme(diag_name, img_file)

# Choice 1: Push to your IIoT GitHub repo
# palette.push_to_github('.')

# Choice 2: Upload to your S3 Documentation bucket
# palette.upload_to_s3([img_file, 'README.md'], 'my-iiot-docs-bucket')
