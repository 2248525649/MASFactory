#!/usr/bin/env bash
set -euo pipefail

APP_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
HOST="${CLAWCANVAS_HOST:-0.0.0.0}"
PORT="${CLAWCANVAS_PORT:-15051}"
WORKERS="${CLAWCANVAS_WORKERS:-2}"
TIMEOUT="${CLAWCANVAS_TIMEOUT:-120}"

cd "$APP_DIR/frontend"
npm ci
npm run build

cd "$APP_DIR/backend"
if ! python -m pip --version >/dev/null 2>&1; then
  python -m ensurepip --upgrade
fi
python -m pip install -r requirements.txt
exec python -m gunicorn "clawcanvas_backend.app:create_app()" \
  --bind "${HOST}:${PORT}" \
  --workers "${WORKERS}" \
  --timeout "${TIMEOUT}"
