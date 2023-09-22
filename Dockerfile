FROM python:latest

WORKDIR /app

COPY . .

RUN apt-get update && apt-get install -y --no-install-recommends \
    ca-certificates curl firefox-esr tor          \
 && rm -fr /var/lib/apt/lists/*                \
 && curl -L https://github.com/mozilla/geckodriver/releases/download/v0.33.0/geckodriver-v0.33.0-linux64.tar.gz | tar xz -C /usr/local/bin \
 && apt-get purge -y ca-certificates curl

RUN pip install --upgrade pip && pip install .

ENTRYPOINT ["tor2tor"]
