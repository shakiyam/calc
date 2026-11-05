FROM python:3.15-slim-trixie
# TODO: Remove package upgrades once base image includes apt and libapt-pkg7.0 >= 3.0.4 (CVE-2026-109518)
# hadolint ignore=DL3008
RUN apt-get update \
  && apt-get -y --no-install-recommends --only-upgrade install apt libapt-pkg7.0 \
  && rm -rf /var/lib/apt/lists/*
RUN mkdir -p /opt/calc
WORKDIR /opt/calc
COPY requirements.txt .
# pip comes from the base image and is unused at runtime; removing it clears trivy findings in its bundled libraries
RUN --mount=from=ghcr.io/astral-sh/uv:0.13,source=/uv,target=/bin/uv \
  uv pip install --system --no-cache -r requirements.txt \
  && uv pip uninstall --system pip
COPY pyproject.toml .
COPY src ./src
RUN --mount=from=ghcr.io/astral-sh/uv:0.13,source=/uv,target=/bin/uv \
  uv pip install --system --no-cache --no-deps .
ARG SOURCE_COMMIT
LABEL org.opencontainers.image.revision=$SOURCE_COMMIT
ENTRYPOINT ["calc"]
