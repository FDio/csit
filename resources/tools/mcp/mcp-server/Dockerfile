ARG BASE_IMAGE=ghcr.io/astral-sh/uv:python3.13-trixie-slim

FROM ${BASE_IMAGE}

# Keep runtime writable paths away from /root for host UID/GID execution.
ENV HOME=/home/csit-mcp \
    PYTHONDONTWRITEBYTECODE=1 \
    UV_CACHE_DIR=/tmp/uv-build-cache \
    UV_TOOL_BIN_DIR=/usr/local/bin

RUN mkdir -p /app "${HOME}" "${HOME}/cache" "${UV_CACHE_DIR}" \
        /tmp/uv-runtime-cache \
    && chmod 0777 "${HOME}" "${HOME}/cache" "${UV_CACHE_DIR}" \
        /tmp/uv-runtime-cache

WORKDIR /app

# Install locked dependencies before copying application source for better
# Docker layer reuse.
COPY .python-version pyproject.toml uv.lock ./
RUN apt-get update \
    && apt-get install --no-install-recommends --yes build-essential \
    && uv sync --locked --no-install-project \
    && apt-get purge --auto-remove --yes build-essential \
    && rm -rf /var/lib/apt/lists/*

COPY . .

ENV UV_CACHE_DIR=/tmp/uv-runtime-cache

EXPOSE 8000

ENTRYPOINT ["uv", "run", "--no-sync", "fastapi", "run", "server.py", "--host", "0.0.0.0", "--port", "8000"]
