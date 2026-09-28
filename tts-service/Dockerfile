FROM python:3.11-slim

RUN apt-get update && apt-get install -y \
    wget \
    curl \
    ffmpeg \
    espeak-ng \
    libespeak-ng1 \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /opt/piper
RUN wget -q https://github.com/rhasspy/piper/releases/download/v1.2.0/piper_amd64.tar.gz \
    && tar -xzf piper_amd64.tar.gz \
    && rm piper_amd64.tar.gz \
    && ln -s /opt/piper/piper/piper /usr/local/bin/piper

WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY app/ ./app/
COPY scripts/ ./scripts/

RUN chmod +x scripts/download_voices.sh && ./scripts/download_voices.sh

EXPOSE 8000

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]