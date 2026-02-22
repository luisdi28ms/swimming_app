# Use a stable version
FROM python:3.12-slim

# 1. System updates & UV installation
COPY --from=ghcr.io/astral-sh/uv:latest /uv /uvx /bin/

RUN apt-get update && apt-get upgrade --yes && \
    apt-get install -y --no-install-recommends curl && \
    rm -rf /var/lib/apt/lists/*

# 2. Security: Non-root user
RUN useradd --create-home deployer
WORKDIR /home/deployer

RUN mkdir -p /home/deployer/data && chown deployer:deployer /home/deployer/data

USER deployer

# 3. Dependency Management
COPY --chown=deployer pyproject.toml uv.lock ./
RUN uv sync --frozen --no-cache --no-dev

# 4. Copy Source Code
COPY --chown=deployer src/ src/

RUN mkdir -p /home/deployer/data && \
    mkdir -p /home/deployer/uploads && \
    chown -R deployer:deployer /home/deployer/data /home/deployer/uploads
# 5. Runtime Configuration
# Point the PATH to the uv-created virtualenv
ENV PATH="/home/deployer/.venv/bin:$PATH"
ENV PYTHONUNBUFFERED=1

ENV DATABASE_URL=sqlite:////home/deployer/data/swimmers.db

# Heroku/Standard dynamic port binding
CMD uv run gunicorn --bind 0.0.0.0:${PORT:-8000} src.main:app
