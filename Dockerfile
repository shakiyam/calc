FROM python:3.14-slim-bookworm
COPY --from=ghcr.io/astral-sh/uv:latest /uv /bin/uv
RUN mkdir -p /opt/calc
WORKDIR /opt/calc
COPY requirements.txt .
RUN uv pip install --system --no-cache -r requirements.txt
COPY pyproject.toml .
COPY src ./src
RUN uv pip install --system --no-cache --no-deps .
ARG SOURCE_COMMIT
ENV SOURCE_COMMIT=$SOURCE_COMMIT
ENTRYPOINT ["calc"]
