FROM ghcr.io/oracle/oraclelinux:9-slim
COPY --from=ghcr.io/astral-sh/uv:latest /uv /bin/uv
# hadolint ignore=DL3041
RUN microdnf -y install python3.12 \
  && microdnf clean all \
  && rm -rf /var/cache
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
