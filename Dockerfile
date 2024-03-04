FROM python:latest

WORKDIR /app

COPY . .

RUN apt-get update && \
    apt-get install -y --no-install-recommends \
    ca-certificates \
    curl \
    firefox-esr \
    tor && \
    rm -fr /var/lib/apt/lists/*

RUN curl -L https://github.com/mozilla/geckodriver/releases/download/v0.34.0/geckodriver-v0.34.0-linux64.tar.gz | \
    tar xz -C /usr/bin && \
    apt-get purge -y \
    ca-certificates \
    curl

RUN pip install --upgrade pip && pip install .

ENTRYPOINT ["tor2tor"]
