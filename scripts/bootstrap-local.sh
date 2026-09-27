#!/usr/bin/env bash
set -euo pipefail; source "$(dirname "$0")/lib.sh"; require_python; mkdir -p "$STATE"
if [[ ! -f "$STATE/device-token" ]]; then "$PYTHON" -c 'import secrets; print(secrets.token_urlsafe(32))' > "$STATE/device-token"; fi
DEVICE_TOKEN="$(<"$STATE/device-token")"
"$PYTHON" "$ROOT/scripts/build_packages.py"
start control-plane env EDGE_DEVICE_TOKEN="$DEVICE_TOKEN" EDGE_STATE_DIR="$STATE" EDGE_PACKAGES_DIR="$ROOT/models/packages" "$PYTHON" -m edge_platform.serve control-plane --port "$CP"; wait_url "http://127.0.0.1:$CP/healthz" control-plane
start cloud env EDGE_PACKAGES_DIR="$ROOT/models/packages" "$PYTHON" -m edge_platform.serve cloud --port "$CLOUD"; wait_url "http://127.0.0.1:$CLOUD/healthz" cloud-fixture
for data in 'device-001 laptop-high 18110' 'device-002 laptop-high 18111' 'device-003 mobile-high 18112' 'device-004 mobile-low 18113' 'device-005 offline-simulated 18114 offline'; do read -r id profile port mode <<<"$data"; args=(--id "$id" --profile "$profile" --port "$port" --state "$STATE/$id" --control-plane "http://127.0.0.1:$CP" --cloud "http://127.0.0.1:$CLOUD"); [[ "${mode:-}" == offline ]] && args+=(--offline); start "$id" env EDGE_DEVICE_TOKEN="$DEVICE_TOKEN" "$PYTHON" -m edge_platform.agent "${args[@]}"; wait_url "http://127.0.0.1:$port/healthz" "$id"; done
echo "fleet ready: control-plane http://127.0.0.1:$CP/"
