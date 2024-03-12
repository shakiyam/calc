FROM container-registry.oracle.com/os/oraclelinux:9-slim
# hadolint ignore=DL3041
RUN microdnf -y install python3.11 python3.11-pip \
  && microdnf clean all \
  && rm -rf /var/cache
RUN mkdir -p /opt/calc
WORKDIR /opt/calc
COPY requirements.txt .
# hadolint ignore=DL3013
RUN python3.11 -m pip install --no-cache-dir --upgrade pip && python3.11 -m pip install --no-cache-dir -r requirements.txt
COPY calc.py .
ENTRYPOINT ["python3.11", "calc.py"]
