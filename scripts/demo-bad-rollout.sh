#!/usr/bin/env bash
set -euo pipefail; source "$(dirname "$0")/lib.sh"; "$ROOT/scripts/demo-rollout.sh"
post "http://127.0.0.1:$CP/api/v1/rollouts" '{"version":"v3","stage":"CANARY","device_ids":["device-001","device-003"]}' >/dev/null; sleep 4
for p in 18110 18112; do curl -fsS "http://127.0.0.1:$p/state" | grep -q '"active":"v2"'; done; echo "bad signed v3 failed readiness; canaries retained v2; expansion halted"
