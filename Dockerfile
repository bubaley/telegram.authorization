FROM ghcr.io/astral-sh/uv:python3.13-bookworm-slim AS builder
ENV UV_COMPILE_BYTECODE=1 UV_LINK_MODE=copy UV_PYTHON_DOWNLOADS=0

WORKDIR /app
RUN --mount=type=cache,target=/root/.cache/uv \
    --mount=type=bind,source=uv.lock,target=uv.lock \
    --mount=type=bind,source=pyproject.toml,target=pyproject.toml \
    uv sync --locked --no-install-project --no-dev
COPY . /app
RUN --mount=type=cache,target=/root/.cache/uv \
    uv sync --locked --no-dev

# ---------------------- #

FROM python:3.13-slim-bookworm

ARG USER_ID=1000
ARG GROUP_ID=1000

RUN apt-get update && apt-get install -y --no-install-recommends \
    make \
    netcat-openbsd \
    && rm -rf /var/lib/apt/lists/*

RUN groupadd -g $GROUP_ID app && useradd -m -u $USER_ID -g app app
WORKDIR /app
COPY --from=builder --chown=app:app /app /app
COPY --chmod=755 wait-for /usr/local/bin/wait-for
USER app

ENV PATH="/app/.venv/bin:$PATH"
EXPOSE 8000
CMD ["gunicorn", "app.main:app", "--bind", "0.0.0.0:8000", "--workers", "4", "-k", "uvicorn.workers.UvicornWorker"]
