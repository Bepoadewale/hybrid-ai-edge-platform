#!/usr/bin/env bash
set -euo pipefail; source "$(dirname "$0")/lib.sh"; "$ROOT/scripts/smoke.sh"
post "http://127.0.0.1:$CP/api/v1/rollouts" '{"version":"v1","stage":"BASELINE","device_ids":["device-001","device-002","device-003","device-004"]}' >/dev/null
for p in 18110 18111 18112 18113; do wait_state "$p" v1; done
local="$(post http://127.0.0.1:18110/v1/infer '{"input":[1,0],"data_classification":"public","routing_profile":"LOCAL_PREFERRED"}')"; echo "local inference: $local"; [[ "$local" == *'"LOCAL"'* ]] || exit 1
cloud="$(post http://127.0.0.1:18113/v1/infer '{"input":[1,0],"data_classification":"public","routing_profile":"LOCAL_PREFERRED","required_version":"v2"}')"; echo "cloud fallback: $cloud"; [[ "$cloud" == *'"CLOUD"'* ]] || exit 1
status="$(curl -sS -o "$STATE/privacy.json" -w '%{http_code}' -X POST http://127.0.0.1:18113/v1/infer -H 'Content-Type: application/json' -d '{"input":[1,0],"data_classification":"restricted","routing_profile":"LOCAL_ONLY","required_version":"v2"}')"; [[ "$status" == 403 ]] || exit 1; echo "privacy denial: HTTP 403; cloud was not invoked"
