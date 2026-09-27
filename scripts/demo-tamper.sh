#!/usr/bin/env bash
set -euo pipefail; source "$(dirname "$0")/lib.sh"; "$ROOT/scripts/demo-rollout.sh"
"$PYTHON" "$ROOT/scripts/demo-tamper.py" "$ROOT/models/packages/classifier-v4.zip"
post "http://127.0.0.1:$CP/api/v1/rollouts" '{"version":"v4","stage":"CANARY","device_ids":["device-002"]}' >/dev/null; sleep 3
curl -fsS http://127.0.0.1:18111/state | grep -q '"active":"v2"'; curl -fsS http://127.0.0.1:18111/state | grep -q '"activation":"ROLLED_BACK"'; echo "tampered v4 rejected before activation; v2 remains known-good"
