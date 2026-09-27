#!/usr/bin/env bash
set -euo pipefail; source "$(dirname "$0")/lib.sh"
if [[ -d "$STATE" ]]; then for f in "$STATE"/*.pid; do [[ -f "$f" ]] && kill "$(cat "$f")" 2>/dev/null || true; done; rm -rf "$STATE"; fi
rm -rf "$ROOT/models/packages"; echo "teardown complete: only hybrid-ai-edge-platform state, packages, and agent processes were removed"
