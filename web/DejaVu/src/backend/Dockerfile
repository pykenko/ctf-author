FROM python:3.10-slim

WORKDIR /app

ARG EXIFTOOL_VERSION=12.23
RUN apt-get update \
    && apt-get install -y --no-install-recommends perl wget tar ca-certificates \
    && mkdir -p /opt/exiftool \
    && wget -qO- "https://github.com/exiftool/exiftool/archive/refs/tags/${EXIFTOOL_VERSION}.tar.gz" \
        | tar -xz --strip-components=1 -C /opt/exiftool \
    && cp /opt/exiftool/exiftool /usr/local/bin/exiftool \
    && cp -r /opt/exiftool/lib /usr/local/bin/lib \
    && rm -rf /var/lib/apt/lists/* \
    && pip install --no-cache-dir flask \
    && useradd -m -u 10001 appuser \
    && printf 'TECHFEST2026{ayomabarisaac}\n' > /flag.txt \
    && chown root:root /flag.txt \
    && chmod 0444 /flag.txt \
    && mkdir -p /challenge_tmp \
    && chown appuser:appuser /challenge_tmp

COPY app.py .

USER appuser

EXPOSE 5001

CMD ["python", "app.py"]
