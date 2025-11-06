FROM python:3.10-slim

ENV DEBIAN_FRONTEND=noninteractive

RUN apt-get update && apt-get install -y \
    wget curl gnupg unzip firefox-esr xvfb \
    && rm -rf /var/lib/apt/lists/*

RUN GECKODRIVER_VERSION=0.36.0 && \
    wget -q "https://github.com/mozilla/geckodriver/releases/download/v${GECKODRIVER_VERSION}/geckodriver-v${GECKODRIVER_VERSION}-linux64.tar.gz" && \
    tar -xzf geckodriver-v${GECKODRIVER_VERSION}-linux64.tar.gz && \
    mv geckodriver /usr/local/bin/ && \
    chmod +x /usr/local/bin/geckodriver

WORKDIR /app
COPY . .

RUN pip install --no-cache-dir -r requirements.txt

# Lanzar Firefox dentro de una pantalla virtual (headless real)
CMD xvfb-run -a python boletin_scraper.py
