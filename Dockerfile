FROM docker.io/python:3.11-alpine3.16
COPY requirements.txt /requirements.txt
RUN pip install --no-cache-dir -r /requirements.txt
COPY calc.py /calc.py
ENTRYPOINT ["python", "/calc.py"]
