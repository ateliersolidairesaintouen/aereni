# Même version de Python que celle utilisée aujourd'hui en production (3.7).
# À monter (3.11, 3.12...) quand requirements.txt et le code auront été migrés :
#   docker build --build-arg PYTHON_VERSION=3.11 -t aereni-backend .
ARG PYTHON_VERSION=3.7


# ---- Étape 1 : compilation des dépendances (outils de build, jamais livrés) ----
FROM python:${PYTHON_VERSION}-slim AS builder

RUN apt-get update \
    && apt-get install -y --no-install-recommends build-essential libpq-dev \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /build
COPY requirements.txt .
RUN pip wheel --no-cache-dir --wheel-dir /wheels -r requirements.txt


# ---- Étape 2 : image finale ----
FROM python:${PYTHON_VERSION}-slim

RUN apt-get update \
    && apt-get install -y --no-install-recommends libpq5 \
    && rm -rf /var/lib/apt/lists/* \
    && useradd --system --create-home --uid 10001 aereni

WORKDIR /app

COPY --from=builder /wheels /wheels
COPY requirements.txt .
RUN pip install --no-cache-dir --no-index --find-links=/wheels -r requirements.txt \
    && rm -rf /wheels

COPY aereni ./aereni

# La configuration (mot de passe de la base, etc.) n'est jamais copiée dans l'image :
# elle se monte au lancement sur /config/aereni.cfg.
# AERENI_HOST=0.0.0.0 est nécessaire dans un conteneur ; limite l'exposition côté hôte
# avec -p 127.0.0.1:5000:5000.
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    AERENI_CONFIG=/config/aereni.cfg \
    AERENI_HOST=0.0.0.0 \
    AERENI_PORT=5000

USER aereni
EXPOSE 5000

HEALTHCHECK --interval=30s --timeout=10s --start-period=20s --retries=3 \
    CMD python -c "import urllib.request; urllib.request.urlopen('http://127.0.0.1:5000/stats/last_measurement', timeout=5)" || exit 1

CMD ["python", "-m", "aereni.app"]
