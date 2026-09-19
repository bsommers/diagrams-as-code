# Diagrams as Code - How to Run

## installing and running

### virtual env

python -m venv venv
source venv/bin/activate

### pip install requiremnents
pip install -r requirements.txt

### or indivudally:

### install
```
pip install diagrams
pip install pyyaml
pip install gitpython boto3
```
###  turn this into requirements.txt

### run
`python hivemq_diagram.py`

## How to use Github Actions:

# How to use this as a Technical Account Manager
Imagine you are at a client site or working from home in Baltimore. You realize the customer needs a new Kafka consumer added to the architecture.

- Edit `icons.yaml`: Add the Kafka symbol if it's not there.
- Edit `main.py`: Add one line: `broker >> palette.get_node("kafka", "Enterprise Data Lake")`.
- Git Push: Push the change to GitHub.

Within 60 seconds, the GitHub repository's front page (README.md) will refresh with the updated high-res diagram and a new entry in the Bill of Materials table. No manual rendering required.
