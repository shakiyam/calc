FROM python:3.15-slim-trixie
RUN mkdir -p /opt/calc
WORKDIR /opt/calc
# Sync into the system Python so the tools stay on the default PATH without a venv
ENV UV_PROJECT_ENVIRONMENT=/usr/local
COPY pyproject.toml uv.lock ./
RUN --mount=from=ghcr.io/astral-sh/uv:0.13,source=/uv,target=/bin/uv \
  uv sync --locked --no-cache --no-install-project --extra dev
COPY src ./src
COPY tests ./tests
RUN --mount=from=ghcr.io/astral-sh/uv:0.13,source=/uv,target=/bin/uv \
  uv sync --locked --no-cache --no-editable --extra dev
ARG SOURCE_COMMIT
LABEL org.opencontainers.image.revision=$SOURCE_COMMIT
CMD ["/bin/bash"]
