ARG BASE_IMAGE=ghcr.io/astral-sh/uv:python3.13-trixie-slim

FROM ${BASE_IMAGE}

# Keep runtime writable paths away from /root for host UID/GID execution.
ENV HOME=/home/csit-mcp \
    PYTHONDONTWRITEBYTECODE=1 \
    UV_CACHE_DIR=/tmp/uv-build-cache \
    UV_TOOL_BIN_DIR=/usr/local/bin

RUN mkdir -p /app "${HOME}" "${UV_CACHE_DIR}" /tmp/uv-runtime-cache \
    && chmod 0777 "${HOME}" "${UV_CACHE_DIR}" /tmp/uv-runtime-cache

WORKDIR /app

# Install locked dependencies before copying application source for better
# Docker layer reuse.
COPY .python-version pyproject.toml uv.lock ./
RUN uv sync --locked --no-install-project

COPY . .

ENV UV_CACHE_DIR=/tmp/uv-runtime-cache

EXPOSE 7860

ENTRYPOINT ["uv", "run", "--no-sync", "app.py"]
