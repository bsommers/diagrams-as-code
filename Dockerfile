# Use a slim Python image
FROM python:3.11-slim

# Install Graphviz system dependencies
RUN apt-get update && apt-get install -y \
    graphviz \
    libgraphviz-dev \
    pkg-config \
    git \
    && rm -rf /var/lib/apt/lists/*

# Set the working directory
WORKDIR /app

# Copy requirements and install
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy the rest of your code and assets
COPY . .

# Command to run your main script
CMD ["python", "main.py"]
