#!/usr/bin/env bash
set -euo pipefail; source "$(dirname "$0")/lib.sh"; "$ROOT/scripts/demo-fleet.sh"
post "http://127.0.0.1:$CP/api/v1/rollouts" '{"version":"v2","stage":"CANARY","device_ids":["device-001","device-003"]}' >/dev/null
for p in 18110 18112; do wait_state "$p" v2; done; echo "canary v2 active on representative laptop/mobile profiles"
post "http://127.0.0.1:$CP/api/v1/rollouts" '{"version":"v2","stage":"EXPAND","device_ids":["device-002","device-004","device-005"]}' >/dev/null
wait_state 18111 v2; wait_state 18113 v1; echo "expanded: compatible laptop updated; mobile-low retained v1"
post http://127.0.0.1:18114/admin/online '{"online":true}' >/dev/null; post http://127.0.0.1:18114/admin/reconcile '{}' >/dev/null; wait_state 18114 v2; echo "offline agent reconnected and reconciled v2"
