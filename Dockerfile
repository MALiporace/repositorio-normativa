FROM python:3.10-slim

ENV DEBIAN_FRONTEND=noninteractive

RUN apt-get update && apt-get install -y \
    wget curl unzip gnupg ca-certificates xvfb firefox-esr \
    fonts-liberation libgtk-3-0 libx11-xcb1 libxcb1 libdbus-glib-1-2 libxt6 libxcomposite1 libxdamage1 libxi6 libnss3 libxrandr2 libasound2 \
    && rm -rf /var/lib/apt/lists/*

# Instalar geckodriver
RUN GECKODRIVER_VERSION=0.36.0 && \
    wget -q "https://github.com/mozilla/geckodriver/releases/download/v${GECKODRIVER_VERSION}/geckodriver-v${GECKODRIVER_VERSION}-linux64.tar.gz" && \
    tar -xzf geckodriver-v${GECKODRIVER_VERSION}-linux64.tar.gz && \
    mv geckodriver /usr/local/bin/ && \
    chmod +x /usr/local/bin/geckodriver

WORKDIR /app
COPY . .

RUN pip install --no-cache-dir -r requirements.txt

CMD ["xvfb-run", "--auto-servernum", "--server-args='-screen 0 1024x768x24'", "python", "boletin_scraper.py"]
