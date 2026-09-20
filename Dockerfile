# Use official uv image with Python 3.12 slim
FROM ghcr.io/astral-sh/uv:python3.12-bookworm-slim

# Set working directory
WORKDIR /app

# Enable bytecode compilation and optimize uv for container builds
ENV UV_COMPILE_BYTECODE=1 \
    UV_LINK_MODE=copy \
    PYTHONUNBUFFERED=1

# Install standard DejaVu fonts for crisp SVG/PNG font rendering
RUN apt-get update && apt-get install -y --no-install-recommends \
    fonts-dejavu-core \
    && rm -rf /var/lib/apt/lists/*

# Install project dependencies using frozen lockfile first for optimal layer caching
COPY pyproject.toml uv.lock ./
RUN uv sync --frozen --no-install-project

# Copy application source code and assets
COPY . .

# Sync the root project into virtualenv
RUN uv sync --frozen

# Place the virtualenv on PATH
ENV PATH="/app/.venv/bin:$PATH"

# Default command runs the main architecture diagram generator
CMD ["uv", "run", "python", "main.py"]
