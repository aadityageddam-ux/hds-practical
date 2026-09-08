# Reproduces the Lab 1 environment at the OS level, not just the Python packages.
#
# Build:  docker build -t hds-practical .
# Run:    docker run --rm hds-practical
#
# `docker run` should print the same summary as `uv run python src/analysis.py`
# does natively.

FROM ghcr.io/astral-sh/uv:python3.13-bookworm-slim

WORKDIR /app

# Install dependencies first, from the lockfile only, so this layer is cached
# unless pyproject.toml / uv.lock actually change.
COPY pyproject.toml uv.lock .python-version ./
RUN uv sync --locked --no-install-project

# Then copy the code and data.
COPY src/ ./src/
COPY data/ ./data/

# --no-sync: the environment is already built above; just run the script in it.
CMD ["uv", "run", "--no-sync", "python", "src/analysis.py"]
