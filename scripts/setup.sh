#!/usr/bin/env bash
# Reproducible setup for Open WebUI in this repository.
# Usage: ./scripts/setup.sh
set -euo pipefail

cd "$(dirname "$0")/.."

if [ ! -f .env ]; then
    echo "WARNING: .env not found. Copy .env.example to .env and fill in your own keys:"
    echo "  cp .env.example .env"
fi

echo "[1/2] Creating virtual environment (Python 3.11)..."
uv venv --python 3.11 .venv

echo "[2/2] Installing pinned dependencies from requirements.lock..."
uv pip install --python .venv/bin/python -r requirements.lock

echo
echo "Done. Start Open WebUI with:"
echo "  .venv/bin/open-webui serve"
echo "Then open http://localhost:8080"
