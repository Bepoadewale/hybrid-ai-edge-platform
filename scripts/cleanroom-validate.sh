#!/usr/bin/env bash
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
cd "$ROOT"
make clean-local
make bootstrap-local
make smoke
make demo-fleet
make demo-bad-rollout
make demo-tamper
make demo-offline
make verify
make clean-local
test ! -e .local
echo "clean-room cycle passed: project state and agent processes removed"
