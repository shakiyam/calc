FROM python:3.10-alpine3.15
COPY requirements.txt /requirements.txt
RUN pip install --no-cache-dir -r /requirements.txt
COPY calc.py /calc.py
ENTRYPOINT ["python", "/calc.py"]
