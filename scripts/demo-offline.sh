#!/usr/bin/env bash
set -euo pipefail; source "$(dirname "$0")/lib.sh"; "$ROOT/scripts/demo-fleet.sh"
post http://127.0.0.1:18110/admin/online '{"online":false}' >/dev/null; post http://127.0.0.1:18110/v1/infer '{"input":[1,0],"data_classification":"restricted","routing_profile":"LOCAL_ONLY"}' | grep -q '"LOCAL"'; curl -fsS http://127.0.0.1:18110/state | grep -q '"telemetry_buffered":'; post http://127.0.0.1:18110/admin/online '{"online":true}' >/dev/null; post http://127.0.0.1:18110/admin/reconcile '{}' >/dev/null; echo "offline local inference buffered telemetry and reconnected"
