ARG BASE_IMAGE=ghcr.io/astral-sh/uv:python3.13-trixie-slim

FROM ${BASE_IMAGE}

# Ensure installed tools can be executed out of the box
ENV UV_TOOL_BIN_DIR=/usr/local/bin

# Then, add the rest of the project source code and install it
# Installing separately from its dependencies allows optimal layer caching
COPY . /app

# Sync the project into a new environment, asserting the lockfile is up to date
WORKDIR /app

# RUN uv sync --locked
RUN uv sync

# Presuming there is a `app` command provided by the project
CMD ["uv", "run", "app.py"]