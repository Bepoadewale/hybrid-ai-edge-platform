#!/usr/bin/env bash
set -euo pipefail; source "$(dirname "$0")/lib.sh"; wait_url "http://127.0.0.1:$CP/healthz" control-plane; wait_url "http://127.0.0.1:$CLOUD/healthz" cloud
for p in 18110 18111 18112 18113 18114; do wait_url "http://127.0.0.1:$p/healthz" "agent-$p"; done
devices="$(curl -fsS http://127.0.0.1:$CP/api/v1/devices)"; [[ "$devices" == *device-004* ]] || { echo "registration failed" >&2; exit 1; }
[[ "$(curl -s -o /dev/null -w '%{http_code}' "http://127.0.0.1:$CP/api/v1/devices/device-001/desired")" == "401" ]] || { echo "unauthenticated device request was not rejected" >&2; exit 1; }
echo "smoke passed: control plane, cloud fixture, five independent agents; unauthenticated device request rejected"
