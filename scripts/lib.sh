#!/usr/bin/env bash
set -euo pipefail
ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"; PYTHON="${ROOT}/.venv/bin/python"; STATE="${ROOT}/.local"; CP=18100; CLOUD=18101
require_python(){ test -x "${PYTHON}" || { echo "run make install first" >&2; exit 1; }; }
wait_url(){ local url="$1"; local name="$2"; local deadline=$((SECONDS+30)); until curl -fsS --max-time 2 "$url" >/dev/null 2>&1; do ((SECONDS<deadline)) || { echo "$name unavailable: $url" >&2; exit 1; }; sleep 1; done; }
start(){ local name="$1"; shift; nohup "$@" >"${STATE}/${name}.log" 2>&1 </dev/null & echo $! >"${STATE}/${name}.pid"; }
post(){ curl -fsS --max-time 10 -X POST "$1" -H 'Content-Type: application/json' -d "$2"; }
wait_state(){ local port="$1"; local version="$2"; local deadline=$((SECONDS+30)); until curl -fsS "http://127.0.0.1:${port}/state" | grep -q "\"active\":\"${version}\""; do ((SECONDS<deadline)) || { echo "agent on ${port} did not activate ${version}" >&2; exit 1; }; sleep 1; done; }
