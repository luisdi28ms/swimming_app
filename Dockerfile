# Use a stable version (3.12 or 3.13) as 3.14 is currently in alpha/dev
FROM python:3.12-slim

# 1. System updates & UV installation
COPY --from=ghcr.io/astral-sh/uv:latest /uv /uvx /bin/

RUN apt-get update && apt-get upgrade --yes && \
    apt-get install -y --no-install-recommends curl && \
    rm -rf /var/lib/apt/lists/*

# 2. Security: Non-root user
RUN useradd --create-home deployer
USER deployer
WORKDIR /home/deployer

# 3. Dependency Management
# We don't need to manually create a venv; uv handles it.
COPY --chown=deployer pyproject.toml uv.lock ./
RUN uv sync --frozen --no-cache --no-dev

# 4. Copy Source Code
COPY --chown=deployer src/ src/
COPY --chown=deployer test/ test/

# 5. CI inside Build (Optional but good)
# This ensures the image won't build if tests fail
RUN uv run pytest

# 6. Runtime Configuration
ENV PATH="/home/deployer/.venv/bin:$PATH"
ENV PYTHONUNBUFFERED=1

# Heroku dynamic port binding
CMD uv run gunicorn --bind 0.0.0.0:$PORT src.main:app
