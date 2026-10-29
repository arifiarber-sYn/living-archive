# The Living Archive — stdlib-only Python runtime
FROM python:3.12-slim

WORKDIR /app

# No third-party Python dependencies: the project runs on the standard library.
COPY . .

ENV PYTHONUNBUFFERED=1

# CLI entry point: docker run --rm -e NEBIUS_API_KEY=... image "your question"
# Web UI:      docker run --rm -p 8000:8000 image python3 -m src.server
ENTRYPOINT ["python3", "-m", "src.app"]
