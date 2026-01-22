FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY core core
COPY services services
COPY config config

CMD ["uvicorn", "services.api.app:app", "--host", "0.0.0.0", "--port", "8080", "--log-level", "debug"]

