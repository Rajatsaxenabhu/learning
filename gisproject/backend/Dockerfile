FROM python:3.13.3-slim

ENV DEBIAN_FRONTEND=noninteractive
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1
ENV PYTHONPATH=/home/app


RUN apt-get update && apt-get install -y \
    postgresql-client\
    gdal-bin \
    libgdal-dev \
    libproj-dev \
    libpq-dev \
    binutils \
    gcc \
    build-essential \
    curl \
    wget \
    && rm -rf /var/lib/apt/lists/*


ENV CPLUS_INCLUDE_PATH=/usr/include/gdal
ENV C_INCLUDE_PATH=/usr/include/gdal
ENV GDAL_CONFIG=/usr/bin/gdal-config


RUN groupadd -r appuser && useradd -r -g appuser -u 1000 -m -d /home/appuser appuser

WORKDIR /home/app


COPY --from=ghcr.io/astral-sh/uv:latest /uv /uvx /bin/

ENV UV_COMPILE_BYTECODE=1
ENV UV_LINK_MODE=copy
ENV PATH="/home/app/.venv/bin:$PATH"


COPY pyproject.toml uv.lock* ./


RUN uv sync --frozen --no-install-project --no-dev

COPY . .

RUN chown -R appuser:appuser /home/app

USER appuser

EXPOSE 7000