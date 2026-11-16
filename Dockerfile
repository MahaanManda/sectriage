# SecTriage container. The vector index is built at image build time so the container
# starts fast and never needs the knowledge base at runtime beyond the baked-in index.
FROM python:3.14-slim

ENV PYTHONUNBUFFERED=1 PYTHONDONTWRITEBYTECODE=1 PIP_NO_CACHE_DIR=1

RUN useradd --create-home --uid 10001 app
WORKDIR /app
RUN chown app:app /app

COPY requirements.txt .
RUN pip install -r requirements.txt

COPY --chown=app:app triage.py agent.py api.py ingest.py ./
COPY --chown=app:app knowledge_base ./knowledge_base
COPY --chown=app:app data ./data
COPY --chown=app:app ui ./ui

USER app
# Builds chroma_db and downloads the embedding model into the app user's cache.
RUN python ingest.py

# Secrets are NOT in the image. Provide at runtime:
#   ANTHROPIC_API_KEY (required), TRIAGE_API_TOKEN (recommended), RATE_LIMIT_PER_MIN, DAILY_TRIAGE_LIMIT
ENV PORT=8000
EXPOSE 8000
HEALTHCHECK --interval=30s --timeout=5s --start-period=20s \
  CMD python -c "import os,urllib.request;urllib.request.urlopen('http://127.0.0.1:'+os.environ.get('PORT','8000')+'/health')"

# --proxy-headers lets the per-IP rate limit see the real client IP behind the host's proxy.
CMD ["sh", "-c", "exec uvicorn api:app --host 0.0.0.0 --port ${PORT} --proxy-headers --forwarded-allow-ips='*'"]
