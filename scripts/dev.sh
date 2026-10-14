#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
BACKEND_PORT="${BACKEND_PORT:-8000}"
FRONTEND_PORT="${FRONTEND_PORT:-5173}"
BACKEND_PID=""
FRONTEND_PID=""

cleanup() {
  if [[ -n "${FRONTEND_PID}" ]] && kill -0 "${FRONTEND_PID}" 2>/dev/null; then
    kill "${FRONTEND_PID}" 2>/dev/null || true
  fi

  if [[ -n "${BACKEND_PID}" ]] && kill -0 "${BACKEND_PID}" 2>/dev/null; then
    kill "${BACKEND_PID}" 2>/dev/null || true
  fi
}

trap cleanup EXIT INT TERM

cd "${ROOT_DIR}"

echo "Starting PostgreSQL..."
docker compose up -d postgres

if [[ ! -f backend/.env ]]; then
  echo "Creating backend/.env from example..."
  cp backend/.env.example backend/.env
fi

if [[ ! -f frontend/.env ]]; then
  echo "Creating frontend/.env from example..."
  cp frontend/.env.example frontend/.env
fi

if ! grep -q "VITE_API_BASE_URL=http://localhost:${BACKEND_PORT}" frontend/.env; then
  echo "Using frontend/.env as-is. Make sure VITE_API_BASE_URL points to http://localhost:${BACKEND_PORT}."
fi

cd "${ROOT_DIR}/backend"

if [[ ! -x .venv/bin/python ]]; then
  echo "Creating backend virtual environment..."
  python3 -m venv .venv
fi

source .venv/bin/activate

if [[ ! -f .venv/.requirements-installed || requirements.txt -nt .venv/.requirements-installed ]]; then
  echo "Installing backend dependencies..."
  pip install -r requirements.txt
  touch .venv/.requirements-installed
fi

echo "Starting backend on http://localhost:${BACKEND_PORT} ..."
uvicorn app.main:app --reload --port "${BACKEND_PORT}" &
BACKEND_PID=$!

cd "${ROOT_DIR}/frontend"

if [[ ! -d node_modules ]]; then
  echo "Installing frontend dependencies..."
  npm install
fi

echo "Starting frontend on http://localhost:${FRONTEND_PORT} ..."
npm run dev -- --host 127.0.0.1 --port "${FRONTEND_PORT}" &
FRONTEND_PID=$!

while true; do
  if ! kill -0 "${BACKEND_PID}" 2>/dev/null; then
    wait "${BACKEND_PID}"
    exit $?
  fi

  if ! kill -0 "${FRONTEND_PID}" 2>/dev/null; then
    wait "${FRONTEND_PID}"
    exit $?
  fi

  sleep 1
done
