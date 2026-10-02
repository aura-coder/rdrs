FROM python:3.12-slim

WORKDIR /app

# System dependencies for psutil / watchdog builds
RUN apt-get update && apt-get install -y --no-install-recommends \
        gcc python3-dev \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

RUN mkdir -p /app/data /app/logs /app/data/sandbox

EXPOSE 8000

CMD ["python", "-m", "app.main"]
