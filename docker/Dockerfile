FROM python:3.11-slim AS base

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1 \
    POETRY_VIRTUALENVS_CREATE=false

# Common system deps for torch, pillow, pdf/tesseract utilities, libmagic, and async drivers
RUN apt-get update && \
    apt-get install -y --no-install-recommends \
      build-essential \
      gcc \
      libgl1 \
      libglib2.0-0 \
      libmagic1 \
      libxml2 \
      libxslt1.1 \
      libpq-dev \
      poppler-utils \
      tesseract-ocr \
      curl \
      ca-certificates && \
    rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Separate layer for dependencies to leverage Docker cache
COPY requirements.txt .
RUN pip install --upgrade pip && pip install -r requirements.txt

FROM python:3.11-slim AS runtime

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    LOG_LEVEL=INFO \
    LOG_DIR=/app/logs

RUN apt-get update && \
    apt-get install -y --no-install-recommends \
      libgl1 \
      libglib2.0-0 \
      libmagic1 \
      libxml2 \
      libxslt1.1 \
      libpq-dev \
      poppler-utils \
      tesseract-ocr \
      curl \
      ca-certificates && \
    rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Copy installed site-packages and binaries from builder
COPY --from=base /usr/local/lib/python3.11 /usr/local/lib/python3.11
COPY --from=base /usr/local/bin /usr/local/bin

# App source
COPY . .

# Create a non-root user for runtime
RUN groupadd -r appuser && useradd -r -g appuser appuser && \
    mkdir -p /app/logs && chown -R appuser:appuser /app
USER appuser

EXPOSE 8000

# Use the app's logging config by keeping uvicorn quiet beyond our dictConfig
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000", "--workers", "2"]
